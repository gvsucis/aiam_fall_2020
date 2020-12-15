<?php
	include 'env/env.php';
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );
	$PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );

	$company = $_POST[ 'company' ];

	if ($company != NULL)
	{

		$command_template = "cd %s; %s -c \"from Models import moveToMainDB; moveToMainDB('%s')\"";
		$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $company );
		
		shell_exec( $exec );
		
		echo "success!\n";
	}
	else
	{
		echo "Failure\n";
	}
?>
