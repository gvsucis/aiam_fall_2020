<?php
	include 'env/env.php';

	$BUILD_PARAMS_DIR = env_get( "BUILD_PARAMS_DIR" );
	$RESULTS_DIR = env_get( "RESULTS_DIR" );
	$FINAL_FORM_FIELD = env_get( "FINAL_FORM_FIELD" );
	$PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );


	$data->company = $_POST[ 'company' ];
	
	$useDriver = false;
	if ( isset( $_POST[ 'useDriver' ] ) )
	{
		$useDriver = true;
	}



	foreach( $_POST as $key => $value )
	{	

		if ( strcmp( $key, "useDriver" ) === 0 )
		{
			continue;
		}
		else
		{
			$data->$key = $value;
		}

		if ( strcmp( $key, $FINAL_FORM_FIELD ) === 0 )
		{
			break;
		}
	}

	$data->useDriver = $useDriver;

	$target = str_replace( ' ', '_', $_POST[ 'company' ] );               

	$filename = $BUILD_PARAMS_DIR . $target . '_params.json';	
	$f = fopen( $filename, 'w' );
	fwrite( $f , json_encode($data) );
	fclose($f);

        $command_template = "cd %s; %s -m scrapy crawl builder -a filename=\"%s\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $filename );

	shell_exec( $exec );
	
	$response = "";
	$results_filename = $RESULTS_DIR . $_POST[ 'company' ] . '-jobs.txt';
	
	$f2 = fopen( $results_filename, 'r' );

	$response = fread($f2, filesize($results_filename));
	fclose($f2);
	echo $response;
?>
