#!/usr/bin/perl -w
###############################################################
#  ========================= INFO ==============================
# NAME:         check_cpu.pl   
# AUTHOR:       Jorge Pla
# ======================= SUMMARY ============================
# Nagios plugin to check CPU on servers
#


use strict;
use Net::SNMP;
use Getopt::Long;

# Nagios specific

my $TIMEOUT = 15;
my %ERRORS=('OK'=>0,'WARNING'=>1,'CRITICAL'=>2,'UNKNOWN'=>3,'DEPENDENT'=>4);

#SNMP Data

# Generic with host-ressource-mib
my $base_proc = "1.3.6.1.2.1.25.3.3.1";   # oid for all proc info
my $proc_id   = "1.3.6.1.2.1.25.3.3.1.1"; # list of processors (product ID)
my $proc_load = "1.3.6.1.2.1.25.3.3.1.2"; # %time the proc was not idle over last minute


#Globals

my $o_host = undef;
my $o_community = undef;
my $o_warn = undef;
my $o_crit = undef;
my $o_port = 161;
my $o_timeout = 5;


#Functions

sub print_usage {
	print "Usage: $0 -H <host> -C <snmp_community> -w <warning> -c <critical>\n"
}

sub check_options {
	Getopt::Long::Configure ("bundling");
	GetOptions(
		'H:s' => \$o_host,	'C:s' => \$o_community,
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


# Connect to host
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


# Get description table
my $resultat = (Net::SNMP->VERSION lt 4) ?
	  $session->get_table($base_proc)
	: $session->get_table(Baseoid => $base_proc);

if (!defined($resultat)) {
   printf("ERROR: Description table : %s.\n", $session->error);
   $session->close;
   exit $ERRORS{"UNKNOWN"};
}

$session->close;

my ($cpu_used, $ncpu) = (0,0);
foreach my $key (keys %$resultat) {
	#verb("OID : $key, Desc : $$resultat{$key}");
	if ($key =~ /$proc_load/) {
		$cpu_used += $$resultat{$key};
		$ncpu ++;	
	} 
}

if ($ncpu==0) {
  print "Can't find CPU usage information : UNKNOWN\n";
  exit $ERRORS{"UNKNOWN"};
}

#Calculate average CPU usage
$cpu_used /= $ncpu;
my $exit_val = undef;

print "$ncpu CPU, ", $ncpu==1 ? "load" : "average load";
printf(" %.1f%%", $cpu_used);
$exit_val = $ERRORS{"OK"};

if ($cpu_used > $o_crit) {
	print " > $o_crit% : CRITICAL\n";
	$exit_val = $ERRORS{"CRITICAL"}; 	
} else {
	if ($cpu_used > $o_warn) {
		print " > $o_warn% : WARNING\n";			
		$exit_val = $ERRORS{"WARNING"};
	}
}

print " < $o_warn% : OK\n" if ($exit_val eq $ERRORS{"OK"});
exit $exit_val













