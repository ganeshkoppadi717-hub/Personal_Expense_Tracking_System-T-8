// Small helpers: confirm before destructive actions, and basic client-side checks.
document.addEventListener("DOMContentLoaded", function () {
  var chartColors = ["#6d8ed6", "#73b89f", "#e7a27c", "#9a8bce", "#e1bf69",
    "#78aebe", "#d68191", "#8ba77b", "#d28ba9", "#8291a7"];

  function svgElement(name, attributes, text) {
    var element = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.keys(attributes || {}).forEach(function (key) {
      element.setAttribute(key, attributes[key]);
    });
    if (text !== undefined) {
      element.textContent = text;
    }
    return element;
  }

  function chartData(id) {
    var element = document.getElementById(id);
    if (!element) {
      console.error("Interactive chart data is missing:", id);
      return null;
    }
    try {
      var data = JSON.parse(element.textContent);
      if (!Array.isArray(data)) {
        throw new TypeError("Chart data must be an array.");
      }
      return data;
    } catch (error) {
      console.error("Could not read interactive chart data:", id, error);
      return null;
    }
  }

  function formatMoney(value, currency) {
    return currency + Number(value).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  function attachChartDetail(target, tooltip, message) {
    var show = function () {
      tooltip.textContent = message;
      tooltip.classList.add("is-visible");
    };
    var clear = function (event) {
      if (event && event.type === "focusout" && target.contains(event.relatedTarget)) {
        return;
      }
      tooltip.classList.remove("is-visible");
    };
    target.addEventListener("pointerenter", show);
    target.addEventListener("focusin", show);
    target.addEventListener("pointerleave", clear);
    target.addEventListener("focusout", clear);
  }

  function renderCategoryChart(container, tooltip) {
    var data = chartData("category-chart-data");
    if (!data) {
      return;
    }
    if (!data.length) {
      container.textContent = "No category data to display.";
      return;
    }

    var total = data.reduce(function (sum, item) {
      return sum + Number(item.total || 0);
    }, 0);
    var svg = svgElement("svg", {
      viewBox: "0 0 520 400",
      class: "donut-chart",
      role: "group",
      "aria-label": "Spending by category"
    });
    var group = svgElement("g", { transform: "rotate(-90 200 200)" });
    var radius = 145;
    var circumference = 2 * Math.PI * radius;
    var offset = 0;

    data.forEach(function (item, index) {
      var amount = Number(item.total || 0);
      var share = total > 0 ? amount / total : 0;
      var segment = svgElement("circle", {
        cx: 200,
        cy: 200,
        r: radius,
        fill: "none",
        stroke: chartColors[index % chartColors.length],
        "stroke-width": 34,
        "stroke-dasharray": (circumference * share) + " " + circumference,
        "stroke-dashoffset": -offset,
        class: "donut-segment",
        tabindex: "0",
        "aria-label": item.category + ": " + formatMoney(amount, container.dataset.currency) +
          ", " + Number(item.percent || 0).toFixed(1) + " percent"
      });
      group.appendChild(segment);
      attachChartDetail(segment, tooltip,
        item.category + " · " + formatMoney(amount, container.dataset.currency) +
        " · " + Number(item.percent || 0).toFixed(1) + "% of spending");
      offset += circumference * share;
    });
    svg.appendChild(group);
    svg.appendChild(svgElement("text", {
      x: 200, y: 190, class: "donut-total-label", "text-anchor": "middle"
    }, "TOTAL"));
    svg.appendChild(svgElement("text", {
      x: 200, y: 225, class: "donut-total", "text-anchor": "middle"
    }, formatMoney(total, container.dataset.currency)));

    var legend = document.createElement("ul");
    legend.className = "chart-legend";
    data.forEach(function (item, index) {
      var entry = document.createElement("button");
      entry.type = "button";
      var marker = document.createElement("span");
      marker.className = "legend-marker";
      marker.style.backgroundColor = chartColors[index % chartColors.length];
      marker.setAttribute("aria-hidden", "true");
      var name = document.createElement("span");
      name.className = "legend-name";
      name.textContent = item.category;
      var value = document.createElement("strong");
      value.className = "legend-value";
      value.textContent = formatMoney(item.total, container.dataset.currency);
      entry.appendChild(marker);
      entry.appendChild(name);
      entry.appendChild(value);
      attachChartDetail(entry, tooltip,
        item.category + " · " + formatMoney(item.total, container.dataset.currency) +
        " · " + Number(item.percent || 0).toFixed(1) + "% of spending");
      legend.appendChild(entry);
    });

    var layout = document.createElement("div");
    layout.className = "donut-layout";
    layout.appendChild(svg);
    layout.appendChild(legend);
    container.appendChild(layout);
  }

  function renderMonthlyChart(container, tooltip) {
    var data = chartData("monthly-chart-data");
    if (!data) {
      return;
    }
    if (!data.length) {
      container.textContent = "No monthly data to display.";
      return;
    }

    var width = Math.max(760, container.clientWidth, data.length * 96 + 120);
    var height = 440;
    var left = 72;
    var right = 24;
    var top = 25;
    var bottom = 68;
    var plotWidth = width - left - right;
    var plotHeight = height - top - bottom;
    var maxValue = Math.max.apply(null, data.map(function (item) {
      return Number(item.total || 0);
    }));
    var gridMax = maxValue > 0 ? maxValue * 1.15 : 1;
    var currency = container.dataset.currency;
    var staticPreview = container.dataset.staticPreview === "true";
    var svg = svgElement("svg", {
      viewBox: "0 0 " + width + " " + height,
      width: width,
      height: height,
      class: "monthly-chart",
      role: "group",
      "aria-label": staticPreview
        ? "Monthly spending chart"
        : "Monthly spending. Select a bar to filter by month."
    });

    for (var tick = 0; tick <= 4; tick += 1) {
      var y = top + plotHeight * tick / 4;
      var value = gridMax * (4 - tick) / 4;
      svg.appendChild(svgElement("line", {
        x1: left, x2: width - right, y1: y, y2: y, class: "chart-gridline"
      }));
      svg.appendChild(svgElement("text", {
        x: left - 9, y: y + 4, class: "chart-axis-label", "text-anchor": "end"
      }, value.toLocaleString(undefined, { maximumFractionDigits: 0 })));
    }

    var slotWidth = plotWidth / data.length;
    var barWidth = Math.min(72, slotWidth * .58);
    data.forEach(function (item, index) {
      var amount = Number(item.total || 0);
      var barHeight = amount > 0 ? amount / gridMax * plotHeight : 0;
      var x = left + slotWidth * index + (slotWidth - barWidth) / 2;
      var y = top + plotHeight - barHeight;
      var dateParts = /^(\d{4})-(\d{2})$/.exec(item.month);
      var monthName = item.month;
      if (dateParts) {
        monthName = new Date(Number(dateParts[1]), Number(dateParts[2]) - 1, 1)
          .toLocaleDateString(undefined, { month: "short", year: "numeric" });
      }
      var bar = svgElement("rect", {
        x: x,
        y: y,
        width: barWidth,
        height: Math.max(barHeight, 1),
        rx: 6,
        class: "monthly-bar",
        fill: chartColors[index % chartColors.length],
        tabindex: staticPreview ? "-1" : "0",
        role: staticPreview ? "img" : "button",
        "aria-label": monthName + ": " + formatMoney(amount, currency) +
          ", " + Number(item.count || 0) + " expenses."
      });
      var detail = monthName + " · " + formatMoney(amount, currency) +
        " · " + Number(item.count || 0) + " expenses";
      attachChartDetail(bar, tooltip, detail +
        (staticPreview ? "" : " · Select to filter this month"));
      var selectMonth = function (month) {
        var match = /^(\d{4})-(0[1-9]|1[0-2])$/.exec(month);
        if (!match) {
          console.error("Could not filter chart by invalid month:", month);
          return;
        }
        var year = Number(match[1]);
        var monthNumber = Number(match[2]);
        var lastDay = new Date(year, monthNumber, 0).getDate();
        var params = new URLSearchParams(window.location.search);
        params.set("start", month + "-01");
        params.set("end", month + "-" + String(lastDay).padStart(2, "0"));
        window.location.assign(window.location.pathname + "?" + params.toString());
      };
      if (!staticPreview) {
        bar.addEventListener("click", function () {
          selectMonth(item.month);
        });
        bar.addEventListener("keydown", function (event) {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            selectMonth(item.month);
          }
        });
      }
      svg.appendChild(bar);
      svg.appendChild(svgElement("text", {
        x: x + barWidth / 2,
        y: height - 23,
        class: "chart-month-label",
        "text-anchor": "middle"
      }, monthName));
    });
    container.appendChild(svg);
  }

  document.querySelectorAll(".interactive-chart").forEach(function (container) {
    var tooltip = container.parentElement.querySelector(".chart-tooltip");
    if (!tooltip) {
      console.error("Interactive chart tooltip is missing.");
      return;
    }
    if (container.dataset.chart === "category") {
      renderCategoryChart(container, tooltip);
    } else if (container.dataset.chart === "monthly") {
      renderMonthlyChart(container, tooltip);
    } else {
      console.error("Unknown interactive chart type:", container.dataset.chart);
    }
  });

  document.querySelectorAll("form.js-confirm").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      var message = form.getAttribute("data-confirm") || "Are you sure?";
      if (!window.confirm(message)) {
        event.preventDefault();
      }
    });
  });

  document.querySelectorAll(".flash-close").forEach(function (button) {
    button.addEventListener("click", function () {
      button.closest(".flash").remove();
    });
  });

  document.querySelectorAll("[data-character-count]").forEach(function (field) {
    var counter = document.getElementById(field.getAttribute("data-character-count"));
    if (!counter) {
      return;
    }

    var updateCount = function () {
      counter.textContent = field.value.length + " / " + field.maxLength;
    };
    field.addEventListener("input", updateCount);
    updateCount();
  });

  var amount = document.getElementById("amount");
  if (amount) {
    amount.addEventListener("input", function () {
      var value = parseFloat(amount.value);
      if (amount.value !== "" && (isNaN(value) || value <= 0)) {
        amount.setCustomValidity("Amount must be greater than zero.");
      } else {
        amount.setCustomValidity("");
      }
    });
  }

  var reset = document.getElementById("reset-filters");
  if (reset) {
    reset.addEventListener("click", function () {
      window.location.href = reset.getAttribute("data-url");
    });
  }
});
