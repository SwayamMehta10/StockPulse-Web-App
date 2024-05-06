$(document).ready(function () {
	function forecast(company, period) {
		$.ajax({
			url: "/forecast-price",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({
				company: company,
				period: period,
			}),
			success: function (response) {
				$("#forecastChart").html(response.plot);
				// $("#inference").html(response.explanation);
				// console.log(response.explanation);
			},
			error: function (xhr, status, error) {
				console.error(error);
			},
		});
	}

	$("#applyButton").click(function () {
		var company = $("#company").val();
		var period = $("#period").val();
		if ($(".hidden").is(":visible")) {
			$(".hidden").toggle();
			$(".hidden").toggle();
		} else {
			$(".hidden").toggle();
		}
		fetchNews(company);
		forecast(company, period);
	});

	function fetchNews(company) {
		$.ajax({
			url: "/news-feed",
			type: "POST",
			contentType: "application/json",
			data: JSON.stringify({
				company: company,
			}),
			success: function (response) {
				let newsFeed = document.getElementById("news-feed");
				newsFeed.innerHTML = "";
				for (let i = 0; i < response.headlines.length; i++) {
					let newsTile = document.createElement("div");
					newsTile.className = "news-tile";

					let headlineLink = document.createElement("a");
					headlineLink.href = response.links[i];
					headlineLink.target = "_blank";
					headlineLink.textContent = response.headlines[i];
					newsTile.appendChild(headlineLink);

					let details = document.createElement("div");
					details.className = "news-details";

					let timestamp = document.createElement("span");
					timestamp.textContent = response.timestamps[i];
					timestamp.className = "news-timestamp";
					details.appendChild(timestamp);

					details.appendChild(document.createTextNode(" • "));

					let source = document.createElement("span");
					source.textContent = response.sources[i];
					source.className = "news-source";
					details.appendChild(source);

					newsTile.appendChild(details);

					newsFeed.appendChild(newsTile);

					$("#sentiment_chart").html(response.plot);
					score = response.score;
					if (score <= -0.6) {
						recommendation = "Strong Sell";
						color = "#8B0000";
					} else if (score <= -0.3) {
						recommendation = "Sell";
						color = "#FF0000";
					} else if (score <= 0.3) {
						recommendation = "Hold";
						color = "#0000FF";
					} else if (score <= 0.6) {
						recommendation = "Buy";
						color = "#90EE90";
					} else {
						recommendation = "Strong Buy";
						color = "#008000";
					}
					$("#sentiment_score").html(
						"Sentiment Score = <b>" +
							score +
							"</b><br/>Recommendation: <b style='color: " +
							color +
							";'>" +
							recommendation +
							"</b>"
					);
				}
			},
			error: function (xhr, status, error) {
				console.error("Error fetching news:", error);
			},
		});
	}
});
