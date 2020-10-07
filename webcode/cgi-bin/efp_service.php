<?php
	require_once('jrws.php');
	$result = JRWS::validate('http://www.bar.utoronto.ca/~rbreit/efp/cgi-bin/agi.jdf');
	##if($result==1)
	##{
	##	echo("result is boolean<br>");
	##}
	##echo(sprintf("result=%s<br>",$result));
	##if (!$result)
	##{
	##	JRWS::error("420", "JRWS validation failed<br>");
	##}
	$data = JSON::decode($_REQUEST['request']);
	##echo(print_r($data, true));
	ob_start();
	
	$func = $_REQUEST['function'];
	
	if($func != "" && $func != "efp_short")
	{
		$parameter = $data["efpTuple"];
		$agi = $parameter[0];
		$agi2 = $parameter[1];
		$datasource = $parameter[2];
		$mode = $parameter[3];
		$threshold = $parameter[4];
	}
	else
	{
		$agi = $data['agi'];
		$agi2 = "None";
		$datasource = "Developmental_Map";
		$mode = "Absolute";
		$threshold = 0;
		$func = "efp";
	}
	JRWS::respond(execute($func, $agi, $agi2, $datasource, $mode, $threshold));
	$cont = ob_get_contents();
	ob_end_clean();
	echo $cont;

function execute($fct, $gene, $gene2, $source, $mode, $threshold)
{
	$command = "/usr/bin/python efp_moby.py $fct $gene $gene2 $source $mode $threshold None None";
	exec($command, $output);
	$file = unserialize($output[0]);
	$full_file = "../output/$file";
	$fh = fopen($full_file, 'rb') or die ("Can't open file");
	$content = fread($fh, filesize($full_file));
	return base64_encode($content);
}
?>

