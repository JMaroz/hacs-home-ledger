# Home Ledger

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-custom%20integration-blue.svg)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-custom-orange.svg)](https://hacs.xyz/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Home Ledger is a Home Assistant custom integration for tracking household utility costs, consumption, photovoltaic investments and return on investment.

The current integration documentation covers household utility bill tracking. Photovoltaic investment tracking, ROI, Solarman data and payback analysis are future directions, not available features described here.

## Features

- Track household utility bills for supported utility types.
- Store cost and consumption for each bill period.
- Add, modify and delete bills from Home Assistant service actions.
- Automatically use the expected consumption unit for each utility.
- Expose summary sensors that can be used in dashboards, automations and statistics cards.

## Supported utilities

| Utility       | Consumption unit |
| ------------- | ---------------- |
| `electricity` | `kWh`            |
| `gas`         | `m³`             |
| `water`       | `m³`             |

Home Ledger assigns units automatically from the selected utility type:

- electricity bills use `kWh`;
- gas bills use `m³`;
- water bills use `m³`.

## Installation with HACS

1. Open Home Assistant.
2. Go to **HACS** → **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL.
5. Select **Integration** as the repository category.
6. Search for **Home Ledger** in HACS and install it.
7. Restart Home Assistant when HACS asks you to do so.
8. Go to **Settings** → **Devices & services** → **Add integration** and search for **Home Ledger**.

## Initial configuration

After installation, add Home Ledger from the Home Assistant integrations page:

1. Go to **Settings** → **Devices & services**.
2. Select **Add integration**.
3. Search for **Home Ledger**.
4. Complete the setup form.
5. Submit the form to create the Home Ledger entry.

After the entry is created, use the service actions below to add your utility bills. Each bill should represent one billed period for one supported utility.

## Bill periods and `months`

`months` is the number of months covered by a bill.

Use it to normalize totals and compare bills with different billing periods. For example:

- use `1` for a monthly bill;
- use `2` for a two-month bill;
- use `12` for an annual adjustment bill.

If a bill covers part of a month, enter the decimal value that best represents the period, such as `0.5` for about half a month.

## Managing bills with service actions

Home Ledger service actions are available from **Developer Tools** → **Actions** and can also be used in scripts and automations.

### Add a bill

Use the add bill action to record a new utility bill.

```yaml
service: home_ledger.add_bill
data:
  utility: electricity
  bill_id: electricity_2026_07
  date: "2026-07-31"
  months: 1
  consumption: 312.4
  cost: 86.75
```

Fields:

| Field         | Required | Description                                                                   |
| ------------- | -------- | ----------------------------------------------------------------------------- |
| `utility`     | Yes      | One of `electricity`, `gas` or `water`.                                       |
| `bill_id`     | Yes      | A stable identifier for the bill. Reuse it when editing or deleting the bill. |
| `date`        | Yes      | Bill date or period end date.                                                 |
| `months`      | Yes      | Number of months covered by the bill.                                         |
| `consumption` | Yes      | Consumption value. The unit is automatic from `utility`.                      |
| `cost`        | Yes      | Total bill cost in your Home Assistant currency.                              |

### Modify a bill

Use the modify bill action with the existing `bill_id`. Include the fields that should be changed.

```yaml
service: home_ledger.modify_bill
data:
  bill_id: electricity_2026_07
  months: 1
  consumption: 318.1
  cost: 88.10
```

### Delete a bill

Use the delete bill action with the `bill_id` of the bill to remove.

```yaml
service: home_ledger.delete_bill
data:
  bill_id: electricity_2026_07
```

## Available sensors

Home Ledger exposes sensors for the stored utility data so you can build dashboards and automations around your household costs.

Typical sensors include:

| Sensor                      | Description                                                       |
| --------------------------- | ----------------------------------------------------------------- |
| Total utility cost          | Total cost across stored bills.                                   |
| Electricity cost            | Total electricity cost.                                           |
| Electricity consumption     | Total electricity consumption in `kWh`.                           |
| Gas cost                    | Total gas cost.                                                   |
| Gas consumption             | Total gas consumption in `m³`.                                    |
| Water cost                  | Total water cost.                                                 |
| Water consumption           | Total water consumption in `m³`.                                  |
| Monthly average cost        | Cost normalized by the `months` value across stored bills.        |
| Monthly average consumption | Consumption normalized by the `months` value across stored bills. |

Exact entity IDs depend on the Home Assistant entity registry and the name chosen during setup. Find them in **Settings** → **Devices & services** → **Entities** by filtering for **Home Ledger**.

## Example dashboard

Add a dashboard card that summarizes utility costs and consumption:

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Home Ledger totals
    entities:
      - entity: sensor.home_ledger_total_utility_cost
        name: Total cost
      - entity: sensor.home_ledger_electricity_cost
        name: Electricity cost
      - entity: sensor.home_ledger_gas_cost
        name: Gas cost
      - entity: sensor.home_ledger_water_cost
        name: Water cost
  - type: entities
    title: Consumption
    entities:
      - entity: sensor.home_ledger_electricity_consumption
        name: Electricity
      - entity: sensor.home_ledger_gas_consumption
        name: Gas
      - entity: sensor.home_ledger_water_consumption
        name: Water
```

Adjust the entity IDs to match the entities created in your Home Assistant instance.

## Future direction

Future versions may add photovoltaic investment tracking, return on investment, Solarman-related data and payback analysis. These are not documented as available features in the current README.
