#!/usr/bin/perl -w
###############################################################
#  ========================= INFO ==============================
# NAME:         check_cpu.pl   
# AUTHOR:       Jorge Pla
# ======================= SUMMARY ============================
# Nagios plugin to check Physical Memory on servers
#

use strict;
use Net::SNMP;
use Getopt::Long;

# Nagios specific

my $TIMEOUT = 15;
my %ERRORS=('OK'=>0,'WARNING'=>1,'CRITICAL'=>2,'UNKNOWN'=>3,'DEPENDENT'=>4);

#SNMP Data

#OIDs Generic with host-ressource-mib
my $base_storage_oid = "1.3.6.1.2.1.25.2.3.1";   # oid for hrstorage
my $desc_storage_oid = "1.3.6.1.2.1.25.2.3.1.3";
my $allocated_units_oid = "1.3.6.1.2.1.25.2.3.1.4";
my $storage_size_oid = "1.3.6.1.2.1.25.2.3.1.5";
my $storage_used_oid = "1.3.6.1.2.1.25.2.3.1.6";



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

sub verb { my $t=shift; print $t,"\n"; }

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


# Get desctiption table
my $resultat = (Net::SNMP->VERSION lt 4) ?
	  $session->get_table($desc_storage_oid)
	: $session->get_table(Baseoid => $desc_storage_oid);

if (!defined($resultat)) {
   printf("ERROR: Description table : %s.\n", $session->error);
   $session->close;
   exit $ERRORS{"UNKNOWN"};
}


my $index = q {}; #q funtion used instead of single quotes

foreach my $key (keys %$resultat) {
	#verb("OID : $key, Desc : $$resultat{$key}");
	if ($resultat->{$key} =~ /Physical Memory/) {
		$index = substr $key, -1, 1;
		#verb("index : $index");			
	}
}

#GET RAM VALUES
my $unit_oid = join('.', $allocated_units_oid, $index);
my $size_oid = join('.', $storage_size_oid, $index);
my $used_oid = join('.', $storage_used_oid, $index);

my @oidlists = ($unit_oid, $size_oid, $used_oid);
my $result = (Net::SNMP->VERSION lt 4) ?
	  $session->get_request(@oidlists)
	: $session->get_request(-varbindlist => \@oidlists);

if (!defined($result)) {
   printf("ERROR: Load table : %s.\n", $session->error);
   $session->close;
   exit $ERRORS{"UNKNOWN"};
}

$session->close;  

my $unit = $result->{$unit_oid};
my $size = $result->{$size_oid};
my $used = $result->{$used_oid};

#verb("Unit: $unit, Size: $size, Used: $used");

#Calculate values in GB
my $size_GB = ((($size * $unit) / 1024) / 1024 )/ 1024;
my $used_GB = ((($used * $unit) / 1024) / 1024 )/ 1024;
my $free_GB = $size_GB - $used_GB;
my $used_percent = int(($used / $size)* 100);

#printf("Physical Memory at %d% with %0.2f of %0.2f free\n", $used_percent, $free_GB, $size_GB); 
#Nagios Exit
my $exit_val = undef;

$exit_val = $ERRORS{"OK"};
if ($used_percent > $o_crit) {
    printf("Memory CRITICAL: at %d%% with %0.2f GB of %0.2f GB free\n", $used_percent, $free_GB, $size_GB);
    $exit_val = $ERRORS{"CRITICAL"};
}
if ($used_percent > $o_warn && $used_percent < $o_crit) {
    printf("Memory WARNING: at %d%% with %0.2f GB of %0.2f GB free\n", $used_percent, $free_GB, $size_GB);
    $exit_val = $ERRORS{"WARNING"};
}	
printf("Memory OK: at %d%% with %0.2f GB of %0.2f GB free\n", $used_percent, $free_GB, $size_GB) if ($exit_val eq $ERRORS{"OK"});

exit $exit_val;







