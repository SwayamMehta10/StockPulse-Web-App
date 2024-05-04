$(document).ready(function () {
	function fetchStockData(company, indicator, period, startDate, endDate) {
		$.ajax({
			url: "/fetch-stock-data",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({
				company: company,
				indicator: indicator,
				period: period,
				startDate: startDate,
				endDate: endDate,
			}),
			success: function (response) {
				$("#stockChart").html(response.plot);
				$("#heading").html("StockPulse AI Insights")
				$("#stockAnalysis").html(response.explanation);
				// console.log(response.explanation);
			},
			error: function (xhr, status, error) {
				console.error(error);
			},
		});
	}

	// $("#company").change(function () {
	// 	var company = $(this).val();
	// });

	// $("#indicator").change(function () {
	// 	var indicator = $(this).val();
	// });

	$("#period").change(function () {
		var period = $(this).val();
		if (period === "custom") {
			$("#startDate").prop("disabled", false);
			$("#endDate").prop("disabled", false);
		} else {
			$("#startDate").prop("disabled", true).val("");
			$("#endDate").prop("disabled", true).val("");
		}
	});

	$("#applyButton").click(function () {
		var company = $("#company").val();
		var indicator = $("#indicator").val();
		var period = $("#period").val();
		var startDate = $("#startDate").val();
		var endDate = $("#endDate").val();

		// Fetch stock data
		fetchStockData(company, indicator, period, startDate, endDate);
	});
});
