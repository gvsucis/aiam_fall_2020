       const GET_COMPANY_JOB_RESULTS_SCRIPTNAME = "./get_company_job_results.php";
       async function getCompanyJobResults( company ) {
       	    let data = {}; 
	    await $.ajax({
                type: "GET",
                url: GET_COMPANY_JOB_RESULTS_SCRIPTNAME,
                data: {"company":company},
                success: function(res){
                        data = JSON.parse( res );
         	},
		error: function(err){
			data = {"ERR":"error!\n"}
		}
		});
	 return data
	}
