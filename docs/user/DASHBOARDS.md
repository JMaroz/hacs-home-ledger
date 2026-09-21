# Dashboard and Lovelace Cards

Home Ledger provides comprehensive sensors for costs, consumption, monthly distributions, solar photovoltaic return on investment (ROI), and home maintenance activities.

This guide explains how to build a **100% standalone dashboard** using Home Assistant's native Lovelace cards, as well as optional enhancements with community cards like `apexcharts-card`.

---

## 1. Native vs. Custom Components

| Approach                         | Dependencies           | Highlights                                                                                                                        |
| :------------------------------- | :--------------------- | :-------------------------------------------------------------------------------------------------------------------------------- |
| **Standalone (Native Lovelace)** | 🟢 **None (Built-in)** | Uses native `sections`, `tile`, `gauge`, `entities`, and `markdown` cards. Clean modern look without installing any HACS plugins. |
| **Enhanced (`apexcharts-card`)** | 🟠 **HACS Frontend**   | Adds interactive multi-series monthly bar charts (e.g. comparing electricity, gas, and water costs side-by-side).                 |
| **Mushroom Cards**               | ⚪ **Not needed**      | Home Assistant native `tile` cards provide the same modern, rounded design natively.                                              |

---

## 2. Complete Standalone Dashboard (YAML)

You can copy and paste this complete view into your dashboard using the **Raw Configuration Editor** or by creating a new **Sections View**:

```yaml
title: "Home Ledger"
views:
  - title: "Overview"
    path: "home-ledger-overview"
    icon: "mdi:book-account"
    type: sections
    max_columns: 3
    sections:
      # SECTION 1: Utility Overview & Cost per Unit
      - title: "Utility Overview"
        cards:
          - type: grid
            columns: 2
            square: false
            cards:
              - type: tile
                entity: sensor.total_utility_cost
                name: "Total Utility Cost"
                icon: mdi:cash-multiple
                color: green

              - type: tile
                entity: sensor.electricity_average_monthly_cost
                name: "Avg Electricity / Mo"
                icon: mdi:lightning-bolt
                color: amber

              - type: tile
                entity: sensor.gas_average_monthly_cost
                name: "Avg Gas / Mo"
                icon: mdi:fire
                color: red

              - type: tile
                entity: sensor.water_average_monthly_cost
                name: "Avg Water / Mo"
                icon: mdi:water
                color: blue

          - type: entities
            title: "Cost Efficiency per Unit"
            entities:
              - entity: sensor.electricity_cost_per_unit
                name: "Electricity Unit Cost"
                icon: mdi:flash-outline
              - entity: sensor.gas_cost_per_unit
                name: "Gas Unit Cost"
                icon: mdi:gas-cylinder
              - entity: sensor.water_cost_per_unit
                name: "Water Unit Cost"
                icon: mdi:water-percent

      # SECTION 2: Photovoltaic Return on Investment
      - title: "Solar Photovoltaic ROI"
        cards:
          - type: grid
            columns: 2
            square: false
            cards:
              - type: tile
                entity: sensor.photovoltaic_total_savings
                name: "Cumulative PV Savings"
                icon: mdi:solar-power-variant
                color: green

              - type: tile
                entity: sensor.photovoltaic_payback_period
                name: "Estimated Payback"
                icon: mdi:timer-sand
                color: purple

          - type: tile
            entity: sensor.photovoltaic_break_even_date
            name: "Break-Even Date"
            icon: mdi:calendar-star
            color: teal

          - type: gauge
            entity: sensor.photovoltaic_return_on_investment
            name: "Estimated Annual ROI"
            unit: "%"
            min: 0
            max: 30
            needle: true
            segments:
              - from: 0
                color: "#db4437"
              - from: 5
                color: "#ffa600"
              - from: 10
                color: "#0f9d58"

      # SECTION 3: Dynamic Monthly Tables (Jinja2)
      - title: "Monthly Breakdown"
        cards:
          - type: markdown
            title: "Monthly Cost Ledger"
            content: >
              | Month | ⚡ Electricity | 🔥 Gas | 💧 Water | Total |
              | :--- | :---: | :---: | :---: | :---: |
              {% set elec = state_attr('sensor.total_electricity_cost', 'electricity_monthly_costs') or {} %}
              {% set gas = state_attr('sensor.total_gas_cost', 'gas_monthly_costs') or {} %}
              {% set water = state_attr('sensor.total_water_cost', 'water_monthly_costs') or {} %}
              {% set all_months = (elec.keys() | list + gas.keys() | list + water.keys() | list) | unique | sort(reverse=true) %}
              {% if all_months | length == 0 %}
              *No monthly bills recorded yet.*
              {% else %}
              {% for m in all_months %}
              {% set e = elec.get(m, 0.0) %}
              {% set g = gas.get(m, 0.0) %}
              {% set w = water.get(m, 0.0) %}
              | **{{ m }}** | {{ "€ %.2f"|format(e) }} | {{ "€ %.2f"|format(g) }} | {{ "€ %.2f"|format(w) }} | **{{ "€ %.2f"|format(e + g + w) }}** |
              {% endfor %}
              {% endif %}

          - type: markdown
            title: "Monthly Consumption Ledger"
            content: >
              | Month | ⚡ Electricity (kWh) | 🔥 Gas (m³) | 💧 Water (m³) |
              | :--- | :---: | :---: | :---: |
              {% set elec_c = state_attr('sensor.total_electricity_consumption', 'electricity_monthly_consumption') or {} %}
              {% set gas_c = state_attr('sensor.total_gas_consumption', 'gas_monthly_consumption') or {} %}
              {% set water_c = state_attr('sensor.total_water_consumption', 'water_monthly_consumption') or {} %}
              {% set all_c_months = (elec_c.keys() | list + gas_c.keys() | list + water_c.keys() | list) | unique | sort(reverse=true) %}
              {% if all_c_months | length == 0 %}
              *No consumption data recorded yet.*
              {% else %}
              {% for m in all_c_months %}
              | **{{ m }}** | {{ "%.1f"|format(elec_c.get(m, 0.0)) }} | {{ "%.1f"|format(gas_c.get(m, 0.0)) }} | {{ "%.1f"|format(water_c.get(m, 0.0)) }} |
              {% endfor %}
              {% endif %}

      # SECTION 4: Activities & Maintenance Notes
      - title: "Activities & Notes"
        cards:
          - type: grid
            columns: 2
            square: false
            cards:
              - type: tile
                entity: sensor.latest_activity
                name: "Latest Logged Activity"
                icon: mdi:clipboard-text-clock

              - type: tile
                entity: sensor.total_activities
                name: "Total Activities"
                icon: mdi:format-list-numbered
```

---

## 3. Modular Card Breakdown

If you only want specific individual cards for your existing dashboards:

### Dynamic Monthly Cost Table (Markdown Card)

Reads `electricity_monthly_costs`, `gas_monthly_costs`, and `water_monthly_costs` directly from sensor attributes:

```yaml
type: markdown
title: "Utility Costs by Month"
content: >
  | Month | ⚡ Electricity | 🔥 Gas | 💧 Water | Total |
  | :--- | :---: | :---: | :---: | :---: |
  {% set elec = state_attr('sensor.total_electricity_cost', 'electricity_monthly_costs') or {} %}
  {% set gas = state_attr('sensor.total_gas_cost', 'gas_monthly_costs') or {} %}
  {% set water = state_attr('sensor.total_water_cost', 'water_monthly_costs') or {} %}
  {% set all_months = (elec.keys() | list + gas.keys() | list + water.keys() | list) | unique | sort(reverse=true) %}
  {% for m in all_months %}
  {% set e = elec.get(m, 0.0) %}
  {% set g = gas.get(m, 0.0) %}
  {% set w = water.get(m, 0.0) %}
  | **{{ m }}** | {{ "€ %.2f"|format(e) }} | {{ "€ %.2f"|format(g) }} | {{ "€ %.2f"|format(w) }} | **{{ "€ %.2f"|format(e + g + w) }}** |
  {% endfor %}
```

### Photovoltaic ROI Gauge

Displays the estimated annual ROI percentage:

```yaml
type: gauge
entity: sensor.photovoltaic_return_on_investment
name: "Photovoltaic ROI"
unit: "%"
min: 0
max: 25
needle: true
segments:
  - from: 0
    color: "#db4437"
  - from: 5
    color: "#ffa600"
  - from: 10
    color: "#0f9d58"
```

---

## 4. Optional: Multi-Series Chart with `apexcharts-card` (HACS)

If you have installed [apexcharts-card](https://github.com/RomRider/apexcharts-card) via HACS, you can render monthly bar charts comparing all utilities side-by-side:

```yaml
type: custom:apexcharts-card
header:
  show: true
  title: "Monthly Utility Costs"
  show_states: true
  colorize_states: true
graph_span: 12month
span:
  start: month
  offset: "-11month"
series:
  - entity: sensor.total_electricity_cost
    name: "Electricity"
    type: column
    color: "#ff9800"
    statistics:
      type: state
      period: month
  - entity: sensor.total_gas_cost
    name: "Gas"
    type: column
    color: "#f44336"
    statistics:
      type: state
      period: month
  - entity: sensor.total_water_cost
    name: "Water"
    type: column
    color: "#2196f3"
    statistics:
      type: state
      period: month
```

---

## 5. Automation Blueprints

Ready-to-use blueprints are available in `blueprints/automation/home_ledger/`:

- **[Monthly Bill Reminder](file:///Users/andrea/Repository/hacs-home-ledger/blueprints/automation/home_ledger/monthly_bill_reminder.yaml)**: Sends a mobile notification on a configurable day and time each month.
- **[High Cost Alert](file:///Users/andrea/Repository/hacs-home-ledger/blueprints/automation/home_ledger/high_cost_alert.yaml)**: Alerts when a utility cost sensor exceeds a chosen threshold.
