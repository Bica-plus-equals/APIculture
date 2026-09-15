# Biomass Dashboard to-do list

## 1. Clean up the project

- [ x] Reverse or review the prototype changes I accidentally made.
- [ x] Back up the project.
- [ x] Initialize Git so every future change can be reversed.
- [ x] Remove or protect the Google credentials file.
- [ x] Ignore `.venv`, credentials, `.next`, and `node_modules` in Git.

## 2. Define the output

- [ ] Decide exactly what date the user selects.
- [ ] Define the three KPIs:
  - Temperature and unit
  - Precipitation and unit
  - Wind speed and unit
- [ ] Define the statistics:
  - Total area
  - Pollinizable area
  - Average pollination period
  - Number of clusters
- [ ] Decide what the predicted raster represents.

## 3. Prepare the Python model

- [ ] Move your real Colab/CNN code into a clean Python file.
- [ ] Create one main function such as `run_inference(date)`.
- [ ] Make the function return simple Python values.
- [ ] Test the model independently of the dashboard.
- [ ] Make the model save its predicted GeoTIFF.

## 4. Create the API

- [ ] Create a small Python API using FastAPI.
- [ ] Add a test endpoint such as `/health`.
- [ ] Add an inference endpoint such as `/api/v1/inference`.
- [ ] Make the endpoint accept a date as JSON.
- [ ] Initially return fake results.
- [ ] Test the endpoint using FastAPI's `/docs` page.
- [ ] Replace the fake results with the real model function.

## 5. Connect the frontend

- [ ] Create one TypeScript function that calls the API with `fetch()`.
- [ ] Send the selected date as JSON.
- [ ] Display the returned JSON as plain text first.
- [ ] Add loading and error messages.
- [ ] Confirm that changing the date sends a new request.

## 6. Update the interface

- [ ] Add the date input to the sidebar.
- [ ] Replace Biomass with Temperature.
- [ ] Replace Revenue with Precipitation.
- [ ] Replace Growth Forecast with Wind.
- [ ] Add the pollination statistics box.
- [ ] Clearly label placeholder values.

## 7. Connect the map

- [ ] Fix the current Leaflet loading error.
- [ ] Center the map on the Romanian study area.
- [ ] First display a simple PNG prediction overlay.
- [ ] Add the correct geographic bounds.
- [ ] Later replace the PNG with GeoTIFF or map tiles.
- [ ] Add a legend explaining raster colors.

## 8. Add clustering

- [ ] Put clustering in a separate Python function.
- [ ] Run it after CNN inference.
- [ ] Return the cluster count and statistics through the API.
- [ ] Later display cluster boundaries or colors on the map.

## 9. Test everything

- [ ] Test valid and invalid dates.
- [ ] Test what happens when the Python server is offline.
- [ ] Test when Earth Engine returns no data.
- [ ] Confirm that KPI values match the Python output.
- [ ] Confirm that raster bounds match the study area.
- [ ] Confirm that no credentials reach the browser.

## 10. Add later—not now

- [ ] PostgreSQL database for saved forecasts and jobs.
- [ ] User accounts and authentication.
- [ ] Background processing for slow inference.
- [ ] Download buttons for GeoTIFF and CSV.
- [ ] Deployment and HTTPS.

Your first milestone should be only:

```text
Select date → send HTTP request → Python returns fake JSON → display JSON
```

Once that works, connect the real model and improve the design.
