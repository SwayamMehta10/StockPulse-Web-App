$(document).ready(function () {
	var company, ticker, officialCompanyName;

	function getFinancialStatement(statement_type) {
		$.ajax({
			url: "/get-financial-statement",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({
				ticker: ticker,
				statement_type: statement_type,
			}),
			success: function (data) {
				$("#financial_statement").html(data);
			},
			error: function (xhr, status, error) {
				console.error("Error:", error);
			},
		});
	}

	function getCompanyInfo() {
		$.ajax({
			url: "/get-company-info",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({
				ticker: ticker,
			}),
			success: function (response) {
				company = $("#company").val().split(":");
				officialCompanyName = company[0].trim();
				about = officialCompanyName + " Overview";
				console.log(response);
				$("#company-heading").html(about);
				$("#company-summary").html(response.summary);
				$("#company-website").html("<b>Website:</b> ");
				var link = $("<a>")
					.attr("id", "website-link")
					.html(response.website);
				link.attr("href", response.website);
				$("#company-website").append(link);
				sector = "<b>Sector: </b> " + response.sector;
				$("#company-sector").html(sector);
				industry = "<b>Industry:</b> " + response.industry;
				$("#company-industry").html(industry);
				$("#risk_plot").html(response.risk_plot);
			},
			error: function (xhr, status, error) {
				console.error("Error:", error);
			},
		});
	}

	function getKeyExecutives() {
		$.ajax({
			url: "/get-key-executives",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({
				ticker: ticker,
			}),
			success: function (data) {
				$("#key_executives").html(data);
			},
			error: function (xhr, status, error) {
				console.error("Error:", error);
			},
		});
	}

	$("#applyButton").click(function () {
		var chatbotContainer = document.getElementById("chatbot-container");
		if (chatbotContainer.style.display === "none") {
			chatbotContainer.style.display = "block";
		} else {
			chatbotContainer.style.display = "none";
		}

		company = $("#company").val().split(":");
		ticker = company[1].trim();
		officialCompanyName = company[0].trim();
		if ($(".hidden").is(":visible")) {
			$(".hidden").toggle();
			$(".hidden").toggle();
		} else {
			$(".hidden").toggle();
		}
		getCompanyInfo(ticker);
		document.getElementById("income").click();
		getKeyExecutives(ticker);
	});

	$(
		"#income, #quarterly_income, #cashflow, #balancesheet, #quarterly_balancesheet"
	).click(function () {
		$(
			"#income, #quarterly_income, #cashflow, #balancesheet, #quarterly_balancesheet"
		).removeClass("active");

		$(this).addClass("active");

		var statementType = $(this).attr("id");
		getFinancialStatement(statementType);
	});
});
