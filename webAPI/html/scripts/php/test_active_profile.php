<?php
        include 'env/env.php';
	$PYTHON_VENV_PATH = env_get( "PYTHON_VENV_PATH" );
	$SCRAPE_ENGINE_ROOT_DIR = env_get( "SCRAPE_ENGINE_ROOT_DIR" );

	$company = $_POST[ "company" ];
	$command_template = "cd %s; %s -m scrapy crawl active -a company=\"%s\"";
	$exec = sprintf( $command_template, $SCRAPE_ENGINE_ROOT_DIR, $PYTHON_VENV_PATH, $company );

	shell_exec( $exec );

	echo 1;
?>
