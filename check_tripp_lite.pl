#!/usr/bin/perl -w
###############################################################
#  ========================= INFO ==============================
# NAME:         check_tripp_lite.pl   
# AUTHOR:       Jorge Pla
# ======================= SUMMARY ============================
# Nagios plugin to check Temperature and Humidity on Tripp Lite cooling units using the 
# SNMP Webcard

use strict;
use Net::SNMP;
use Getopt::Long;

# Nagios specific

my $TIMEOUT = 15;
my %ERRORS=('OK'=>0,'WARNING'=>1,'CRITICAL'=>2,'UNKNOWN'=>3,'DEPENDENT'=>4);

#SNMP Data

# Environment Temperature (EnviroSense)
my $env_temp = ".1.3.6.1.4.1.850.101.1.1.2.0";   # oid 

# Environment Humidity 
my $env_humidit = ".1.3.6.1.4.1.850.101.1.2.1.0"; #oid

#Globals

my $o_host = undef;
my $o_community = undef;
my $o_check_type = undef;
my $o_warn = undef;
my $o_crit = undef;
my $o_port = 161;
my $o_timeout = 5;


#Functions

sub print_usage {
	print "Usage: $0 -H <host> -C <snmp_community> -T <temp|hum> -w <warning> -c <critical>\n"
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
} 

#sub verb { my $t=shift; print $t,"\n"; }

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


#Connect to host (SNMP)
sub Get_SNMP_Session {
    my ($session, $error);

    ($session, $error) = Net::SNMP->session(
             -hostname  => $o_host,
             -version   => 1,
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


if($o_check_type eq "temp"){
    
    my $result = Get_SNMP_Values($env_temp);
    my $temp = $result->{$env_temp};

    my $exit_val = undef;
    #Compare with warning and critical temp
    $exit_val = $ERRORS{"OK"};
    if ($temp > $o_crit) {
        print "Temperature is CRITICAL: $temp F\n";
        $exit_val = $ERRORS{"CRITICAL"};
    }
    if ($temp > $o_warn && $temp < $o_crit) {
        print "Temperature Warning: $temp F\n";
        $exit_val = $ERRORS{"WARNING"};
    }	
    print "Temperature is OK: $temp F\n" if ($exit_val eq $ERRORS{"OK"});
    
    exit $exit_val;
}

if($o_check_type eq "hum"){
    
    my $result = Get_SNMP_Values($env_humidit);
    my $hum = $result->{$env_humidit};

    my $exit_val = undef;
    #Compare with warning and critical temp
    $exit_val = $ERRORS{"OK"};
    if ($hum > $o_crit) {
        print "Humidity is CRITICAL: $hum% > $o_crit%\n";
        $exit_val = $ERRORS{"CRITICAL"};
    }
    if ($hum > $o_warn && $hum < $o_crit) {
        print "Humidity Warning: $hum% > $o_warn%\n";
        $exit_val = $ERRORS{"WARNING"};
    }	
    print "Humidity is OK: $hum%\n" if ($exit_val eq $ERRORS{"OK"});
    
    exit $exit_val;
}










