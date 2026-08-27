# Automation and Dashboard Examples

All examples use Home Ledger's actual entity names.

## Automations

### Monthly Bill Reminder

Send a notification on the 5th of each month reminding you to enter last month's bills.

```yaml
alias: "Home Ledger: Monthly bill reminder"
trigger:
  - platform: time
    at: "18:00:00"
condition:
  - condition: time
    day: 5
action:
  - service: notify.notify
    data:
      title: "Home Ledger"
      message: "Don't forget to enter your utility bills for last month."
```

### High Electricity Cost Alert

Alert when total electricity cost exceeds 200 EUR.

```yaml
alias: "Home Ledger: High electricity cost"
trigger:
  - platform: numeric_state
    entity_id: sensor.total_electricity_cost
    above: 200
action:
  - service: notify.notify
    data:
      title: "Home Ledger"
      message: "Electricity cost is {{ states('sensor.total_electricity_cost') }} EUR."
```

### Gas Consumption Threshold

Notify when total gas consumption exceeds 500 m³.

```yaml
alias: "Home Ledger: High gas consumption"
trigger:
  - platform: numeric_state
    entity_id: sensor.total_gas_consumption
    above: 500
action:
  - service: notify.notify
    data:
      title: "Home Ledger"
      message: "Gas consumption is {{ states('sensor.total_gas_consumption') }} m³."
```

### Auto-Add Recurring Bill via Script

Create a script to quickly add a monthly bill from an automation or voice assistant.

```yaml
alias: "Home Ledger: Add electricity bill"
sequence:
  - service: home_ledger.add_bill
    data:
      utility_type: electricity
      months: 1
      total_cost: "{{ cost }}"
      consumption: "{{ consumption }}"
```

Call it:

```yaml
service: script.home_ledger_add_electricity_bill
data:
  cost: 85.50
  consumption: 210.0
```

## Dashboard Cards

### Cost Trend Graph

Track electricity costs over time.

```yaml
type: sensor
entity: sensor.total_electricity_cost
graph: line
name: Electricity Cost
unit: EUR
```

### All Utilities Overview

Combined cost, consumption, and averages in a single glance card.

```yaml
type: glance
title: Home Ledger
entities:
  - entity: sensor.total_utility_cost
    name: Total Cost
  - entity: sensor.total_electricity_cost
    name: Electricity
  - entity: sensor.total_gas_cost
    name: Gas
  - entity: sensor.total_water_cost
    name: Water
```

### Consumption Summary

Bar chart of total consumption per utility.

```yaml
type: entities
title: Consumption
entities:
  - entity: sensor.total_electricity_consumption
    name: Electricity (kWh)
  - entity: sensor.total_gas_consumption
    name: Gas (m³)
  - entity: sensor.total_water_consumption
    name: Water (m³)
```

### Cost Per Unit Comparison

Compare cost efficiency across utilities.

```yaml
type: entities
title: Cost Per Unit
entities:
  - entity: sensor.electricity_cost_per_unit
    name: Electricity (EUR/kWh)
  - entity: sensor.gas_cost_per_unit
    name: Gas (EUR/m³)
  - entity: sensor.water_cost_per_unit
    name: Water (EUR/m³)
```

### History Graph

Track all costs on a single timeline.

```yaml
type: history-graph
title: Utility Costs
hours_to_show: 720
entities:
  - entity: sensor.total_electricity_cost
    name: Electricity
  - entity: sensor.total_gas_cost
    name: Gas
  - entity: sensor.total_water_cost
    name: Water
```

### Average Monthly Cost Bar

Show average monthly cost per utility.

```yaml
type: entities
title: Average Monthly Cost
entities:
  - entity: sensor.electricity_average_monthly_cost
    name: Electricity
  - entity: sensor.gas_average_monthly_cost
    name: Gas
  - entity: sensor.water_average_monthly_cost
    name: Water
```
