       const GET_ALL_JOB_RESULTS_SCRIPTNAME = "/aux/html/scripts/php/get_all_job_results.php";
       // ONLY GRABS ACTIVE JOB RESULTS!!!
	const getCompanyJobResults = async function () {
       	    let data = {}; 
	    await $.ajax({
                type: "GET",
                url: GET_ALL_JOB_RESULTS_SCRIPTNAME,
                success: function(res){
                        data = JSON.parse( res );
         	},
		error: function(err){
			data = {"ERR":"error!\n"}
		}
		});
	 return data
	}
