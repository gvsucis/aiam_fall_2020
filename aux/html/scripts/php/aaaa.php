<?php
	include 'env/env.php';

	$BUILD_PARAMS_DIR = env_get( "BUILD_PARAMS_DIR" );
	$RESULTS_DIR = env_get( "RESULTS_DIR" );
	$PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );


	$filename = $BUILD_PARAMS_DIR . 'XRAY' . '_params.json';	


        $command_template = "cd %s; %s -m scrapy crawl builder -a filename=\"%s\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $filename );

	shell_exec( $exec );
	
	$response = "";
	$results_filename = $RESULTS_DIR . 'XRAY-jobs.txt';
	
	$f2 = fopen( $results_filename, 'r' );

	$response = fread($f2, filesize($results_filename));
	fclose($f2);
	echo $response;
?>
