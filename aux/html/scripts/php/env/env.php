<?php
	function env_get( $variable ){
		// json path relative to php file that is calling this function
		// not this function!
		$data = file_get_contents( 'env/env.json' );
		$json = json_decode( $data, true );
		return $json[ $variable ];
	}
?>
