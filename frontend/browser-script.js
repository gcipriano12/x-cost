
// Definir token no localStorage
localStorage.setItem('access_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUxOTg3NjgzLCJpYXQiOjE3NTE5MDEyODMsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.zjDvC1WRwXbEcuunQLIsB8F8pfI1WyLfu00bg7UmDdc');
console.log('✅ Token set in localStorage');
console.log('Token:', localStorage.getItem('access_token')?.substring(0, 50) + '...');

// Testar a API
fetch('/api/v1/analytics/forecast?months=7', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('access_token'),
    'Content-Type': 'application/json'
  }
})
.then(response => {
  console.log('API Response Status:', response.status);
  if (response.ok) {
    return response.json();
  } else {
    return response.text().then(text => Promise.reject(`${response.status}: ${text}`));
  }
})
.then(data => {
  console.log('✅ API Success:', data);
  console.log('Forecast points:', data.data?.forecast_data?.length);
})
.catch(error => {
  console.log('❌ API Error:', error);
});
