#!/usr/bin/perl -w
###############################################################
#  ========================= INFO ==============================
# NAME:         check_sw_cisco.pl   
# AUTHOR:       Jorge Pla
# ======================= SUMMARY ============================
# Nagios plugin to check CPU, Memory, Temperature, FANS and Power Supplies of Cisco Switches.
#


use strict;
use Net::SNMP;
use Getopt::Long;

# Nagios specific

my $TIMEOUT = 15;
my %ERRORS=('OK'=>0,'WARNING'=>1,'CRITICAL'=>2,'UNKNOWN'=>3,'DEPENDENT'=>4);

#SNMP Data

#CPU
my $cisco_cpu_5s = "1.3.6.1.4.1.9.2.1.56.0"; # Cisco CPU load (5sec %) 
my $cisco_cpu_1m = "1.3.6.1.4.1.9.2.1.57.0"; # Cisco CPU load (1min %)
my $cisco_cpu_5m = "1.3.6.1.4.1.9.2.1.58.0"; # Cisco CPU load (5min %)
  
#MEMORY
my $memory_cpu_used_oid = ".1.3.6.1.4.1.9.9.48.1.1.1.5.1"; # Byte
my $memory_cpu_free_oid = ".1.3.6.1.4.1.9.9.48.1.1.1.6.1"; # Byte
my $memory_io_used_oid = ".1.3.6.1.4.1.9.9.48.1.1.1.5.2"; # Byte
my $memory_io_free_oid = ".1.3.6.1.4.1.9.9.48.1.1.1.6.2"; # Byte

# Temperature
my $temp_oid = ".1.3.6.1.4.1.9.9.13.1.3.1.3"; 

# FANS
my $fans_description = ".1.3.6.1.4.1.9.9.13.1.4.1.2";
my $fans_state = ".1.3.6.1.4.1.9.9.13.1.4.1.3";

# Power supplies
my $ps_description = ".1.3.6.1.4.1.9.9.13.1.5.1.2";
my $ps_state = ".1.3.6.1.4.1.9.9.13.1.5.1.3";


#Globals

my $o_host = undef;
my $o_community = undef;
my $o_warn = undef;
my $o_crit = undef;
my $o_check_type = undef;
my $o_port = 161;
my $o_timeout = 5;
my $exit_val = undef;


##Functions

sub print_usage {
	print "\nUsage: $0 -H <host> -C <snmp_community> -T <cpu|temp|mem|fans|ps> ",
          "-w <warning> -c <critical>\n"
}

sub check_options {
	Getopt::Long::Configure ("bundling");
	GetOptions(
		'H:s' => \$o_host,	'C:s' => \$o_community,
        'T:s' => \$o_check_type,
		'w:s' => \$o_warn,	'c:s' => \$o_crit       
	);

	if (!defined($o_host)) { print_usage(); exit $ERRORS{"UNKNOWN"}}
	if (!defined($o_community)) { print_usage(); exit $ERRORS{"UNKNOWN"}}
	if (!defined($o_check_type)) { print_usage(); exit $ERRORS{"UNKNOWN"}}
    
    ##!ADD expection for warning and critical in some cases
} 


#Connect to host (SNMP)
sub Get_SNMP_Session {
    my ($session, $error);

    ($session, $error) = Net::SNMP->session(
             -hostname  => $o_host,
             -version   => 2,
             -community => $o_community,
             -port      => $o_port,
             -timeout   => $o_timeout
            );

    if (!defined($session)) {
       printf("ERROR opening session: %s.\n", $error);
       exit $ERRORS{"UNKNOWN"};
    }
    return $session;
}

#Get snmp values from OIDs
sub Get_SNMP_Values{
    my $session = Get_SNMP_Session();
    
    my @oidlist = @_;
    my $result = (Net::SNMP->VERSION lt 4) ?
          $session->get_request(@oidlist)
        : $session->get_request(-varbindlist => \@oidlist);

    if (!defined($result)) {
       printf("ERROR: Load table : %s.\n", $session->error);
       $session->close;
       exit $ERRORS{"UNKNOWN"};
    }  
    $session->close; 
    return $result;
}

sub Get_SNMP_Table{
    my $session = Get_SNMP_Session();
    
    my $base_oid = shift;
    
    my $result = (Net::SNMP->VERSION lt 4) ?
	       $session->get_table($base_oid)
	   : $session->get_table(Baseoid => $base_oid);

    if (!defined($result)) {
       printf("ERROR: Description table : %s.\n", $session->error);
       $session->close;
       exit $ERRORS{"UNKNOWN"};
    }
    $session->close; 
    return $result;
}

########## MAIN ###################

check_options();

# Check gobal timeout if snmp screws up
if (defined($TIMEOUT)) {
  alarm($TIMEOUT+5);
} else {
  alarm ($o_timeout+10);
}

$SIG{'ALRM'} = sub {
 print "No answer from host\n";
 exit $ERRORS{"UNKNOWN"};
};



###CPU#####
if($o_check_type eq "cpu"){
    
    my @oid_list = ($cisco_cpu_5s, $cisco_cpu_1m, $cisco_cpu_5m);
    my $result = Get_SNMP_Values(@oid_list);
    
    my @cpu_load = undef;
    
    $cpu_load[0] = $result->{$cisco_cpu_5s};
    $cpu_load[1] = $result->{$cisco_cpu_1m};
    $cpu_load[2] = $result->{$cisco_cpu_5m};
     
    $exit_val=$ERRORS{"OK"};
    for (my $i=0;$i<3;$i++) {
      if ( $cpu_load[$i] > $o_crit ) {
       print " $cpu_load[$i] > $o_crit : CRITICAL";
       $exit_val=$ERRORS{"CRITICAL"};
      }
      if ( $cpu_load[$i] > $o_warn ) {
         # output warn error only if no critical was found
         if ($exit_val eq $ERRORS{"OK"}) {
           print " $cpu_load[$i] > $o_warn : WARNING"; 
           $exit_val=$ERRORS{"WARNING"};
         }
      }
    }
    print "CPU OK - CPU load: $cpu_load[0]%, $cpu_load[1]%, $cpu_load[2]% (1s,1m,5m)\n" if ($exit_val eq $ERRORS{"OK"});

    exit $exit_val;

}


###MEMORY###
if($o_check_type eq "mem"){

    my @oid_list = ($memory_cpu_used_oid, $memory_cpu_free_oid, $memory_io_used_oid,
                    $memory_io_free_oid);
    my $result = Get_SNMP_Values(@oid_list);
    
    my @memory_values = undef;
    
    $memory_values[0] = $result->{$memory_cpu_used_oid};    
    $memory_values[1] = $result->{$memory_cpu_free_oid};    
    $memory_values[2] = $result->{$memory_io_used_oid};    
    $memory_values[3] = $result->{$memory_io_free_oid};    
    
    my $total_cpu_mem = $memory_values[0] + $memory_values[1];
    my $total_io_mem = $memory_values[2] + $memory_values[3];
    
    my $used_mem_cpu_percent = int(($memory_values[0] / $total_cpu_mem) * 100);
    my $used_mem_io_percent = int(($memory_values[2] / $total_io_mem) * 100);
    
    my $free_cpu_mem = sprintf("%0.2f", ($memory_values[1] / 1024) / 1024);
    my $free_io_mem = sprintf("%0.2f", ($memory_values[3] / 1024) / 1024);
    $total_cpu_mem = sprintf("%0.2f", ($total_cpu_mem / 1024) / 1024);
    $total_io_mem = sprintf("%0.2f", ($total_io_mem / 1024) / 1024);
    
    $exit_val = $ERRORS{"OK"};
    #Check for Critical 
    #first print funtion
    sub print_funct {
        my $message = shift;
        my $used_percent = shift;
        my $free = shift;
        my $total = shift;
        
        return print "$message: at $used_percent% with $free GB of $total GB free \n";
    }
    
    if($used_mem_cpu_percent > $o_crit){
        print_funct("Processor Memory CRITICAL", $used_mem_cpu_percent, $free_cpu_mem, $total_cpu_mem);
        $exit_val = $ERRORS{"CRITICAL"}; 
    }
    if($used_mem_io_percent > $o_crit){
        print_funct("I/O Memory CRITICAL", $used_mem_io_percent, $free_io_mem, $total_io_mem);
        $exit_val = $ERRORS{"CRITICAL"}; 
    }
    #Check for Warning
    if($used_mem_cpu_percent > $o_warn && $used_mem_cpu_percent < $o_crit){
        print_funct("Processor Memory WARNING", $used_mem_cpu_percent, $free_cpu_mem, $total_cpu_mem);
        $exit_val = $ERRORS{"WARNING"};
    }
    if($used_mem_io_percent > $o_warn && $used_mem_io_percent < $o_crit){
        print_funct("I/O Memory WARNING", $used_mem_io_percent, $free_io_mem, $total_io_mem);
        $exit_val = $ERRORS{"WARNING"};
    }
    
    #OK
    if($exit_val eq $ERRORS{"OK"}){
        print "MEMORY OK - Processor Memory at $used_mem_cpu_percent% and I/O Memory ",
                "at $used_mem_io_percent%\n";
    }
    
    exit $exit_val;
}

###TEMPERATURE##
if($o_check_type eq "temp"){
 
 my $result = Get_SNMP_Table($temp_oid);
 my $temp = q {};
 
 #just goint to get the first temp value of this table
 #if there are serveral switches stacked, the temp of each one is returned
 foreach my $key ( keys %$result) {
		$temp = $result->{$key};
		last;
 }
 
 #convert temp to Fahrenheit. 
 $temp = ($temp * 1.8) + 32;
 
 $exit_val = $ERRORS{"OK"};
 if($temp > $o_crit){
    print "Temperature CRITICAL: - Temperature is $temp F\n";
    $exit_val = $ERRORS{"CRITICAL"};
 } elsif($temp > $o_warn && $temp < $o_crit){
     print "Temperature WARNING: - Temperature is $temp F\n";
    $exit_val = $ERRORS{"WARNING"};
 } 
 if($exit_val eq $ERRORS{"OK"}){
     print "Temperature: OK - Temperature is $temp F\n";
 }
 
 exit $exit_val;
 
}

##FANS##
if($o_check_type eq "fans"){
    
    my $result = Get_SNMP_Table($fans_state);
    
    my ($num_fans, $state_ok, $state_warn, $state_crit) = (0, 0, 0, 0);
    
    #for every switch in the stack there is a value returned
    #the value returned in the sate of the fan: normal(1), warning(2), critical(3)
    #shutdown(4), notPresent(5), notFunctioning(6)
    foreach my $key (keys %$result){
        my $state = $result->{$key};
        if($state == 1){
            $state_ok ++;
        } elsif($state == 2){
            $state_warn ++;
        } else {
            $state_crit ++;
        }
        $num_fans ++;
    }
    
    $exit_val = $ERRORS{"OK"};
    if($state_crit != 0){
        print "FANS: CRITICAL - $state_crit of $num_fans switches ";
        if($state_crit ==1){print "is "} else{print "are "};
        print "having problems with its fans\n";
        $exit_val = $ERRORS{"CRITICAL"};    
    }elsif($state_warn != 0){
        print "FANS: WARNING - $state_warn of $num_fans switches ";
        if($state_crit ==1){print "is "} else{print "are "};
        print "having problems with its fans\n";
        $exit_val = $ERRORS{"WARNING"};
    }
    if($exit_val eq $ERRORS{"OK"}){
        print "FANS: OK - All the fans are working correctly\n";
    }
    exit $exit_val
}

#Power Supplies
if($o_check_type eq "ps"){

    my $result = Get_SNMP_Table($ps_state);
    
    my ($num_ps, $state_ok, $state_warn, $state_crit) = (0, 0, 0, 0);
    
    #for every switch in the stack there is a value returned
    #the value returned in the sate of the fan: normal(1), warning(2), critical(3)
    #shutdown(4), notPresent(5), notFunctioning(6)
    foreach my $key (keys %$result){
        my $state = $result->{$key};
        if($state == 1){
            $state_ok ++;
        } elsif($state == 2){
            $state_warn ++;
        } else {
            $state_crit ++;
        }
        $num_ps ++;
    }
    
    $exit_val = $ERRORS{"OK"};
    if($state_crit != 0){
        print "Power Supplies: CRITICAL - $state_crit of $num_ps switches ";
        if($state_crit ==1){print "is "} else{print "are "};
        print "having problems with its Power Supplies\n";
        $exit_val = $ERRORS{"CRITICAL"};    
    }elsif($state_warn != 0){
        print "Power Supplies: WARNING - $state_warn of $num_ps switches ";
        if($state_crit ==1){print "is "} else{print "are "};
        print "having problems with its Power Supplies\n";
        $exit_val = $ERRORS{"WARNING"};
    }
    if($exit_val eq $ERRORS{"OK"}){
        print "Power Supplies: OK - All the Power Supplies are working correctly\n";
    }
    exit $exit_val
}








