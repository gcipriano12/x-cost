// Teste da lógica de formatação das datas
const currentDate = new Date();
const currentYear = currentDate.getFullYear(); // 2025
const currentMonth = currentDate.getMonth() + 1; // 7 (Julho)

console.log('📅 Data atual:', { currentYear, currentMonth });

// Dados simulados baseados no resultado do script
const mockData = [
  { month: 'Jul', actual: 749839, forecast: undefined }, // Jul 2024
  { month: 'Aug', actual: 1802709, forecast: undefined }, // Aug 2024  
  { month: 'Sep', actual: 2002619, forecast: undefined }, // Sep 2024
  { month: 'Oct', actual: 2026369, forecast: undefined }, // Oct 2024
  { month: 'Nov', actual: 1848599, forecast: undefined }, // Nov 2024
  { month: 'Dec', actual: 1908035, forecast: undefined }, // Dec 2024
  { month: 'Jan', actual: 2514113, forecast: undefined }, // Jan 2025
  { month: 'Feb', actual: 2584073, forecast: undefined }, // Feb 2025
  { month: 'Mar', actual: 1843097, forecast: undefined }, // Mar 2025
  { month: 'Apr', actual: 2396557, forecast: undefined }, // Apr 2025
  { month: 'May', actual: 3661701, forecast: undefined }, // May 2025
  { month: 'Jun', actual: 6610504, forecast: undefined }, // Jun 2025
  { month: 'Jul', actual: 2013557, forecast: undefined }, // Jul 2025
  { month: 'Jul', actual: undefined, forecast: 3028972 }, // Jul 2025 (forecast)
  { month: 'Aug', actual: undefined, forecast: 3673205 }, // Aug 2025 (forecast)
  { month: 'Sep', actual: undefined, forecast: 3897073 }, // Sep 2025 (forecast)
  { month: 'Oct', actual: undefined, forecast: 3951226 }, // Oct 2025 (forecast)
  { month: 'Nov', actual: undefined, forecast: 3840650 }, // Nov 2025 (forecast)
  { month: 'Dec', actual: undefined, forecast: 3480927 }, // Dec 2025 (forecast)
  { month: 'Jan', actual: undefined, forecast: 3333172 }  // Jan 2026 (forecast)
];

const monthMap = {
  'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
  'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
};

function formatMonthWithYear(monthStr, dataPoint) {
  const monthNum = monthMap[monthStr];
  let year = currentYear;
  
  // Se tem dados atuais (actual), é histórico
  if (dataPoint?.actual !== undefined) {
    // Para dados históricos, se o mês é posterior ao atual, é do ano passado
    if (monthNum > currentMonth) {
      year = currentYear - 1; // 2024
    }
    // Se o mês é anterior ou igual ao atual, é do ano atual (2025)
  } else if (dataPoint?.forecast !== undefined) {
    // Para forecast, se o mês já passou no ano atual, é do próximo ano
    if (monthNum < currentMonth) {
      year = currentYear + 1; // 2026
    }
    // Se o mês é atual ou futuro no ano atual, é do ano atual (2025)
  }
  
  const shortYear = year.toString().slice(-2);
  return `${monthStr}/${shortYear}`;
}

console.log('\n📊 FORMATAÇÃO DOS MESES:');
mockData.forEach((dataPoint, index) => {
  const formatted = formatMonthWithYear(dataPoint.month, dataPoint);
  const type = dataPoint.actual !== undefined ? 'ACTUAL' : 'FORECAST';
  const value = dataPoint.actual || dataPoint.forecast;
  console.log(`${index + 1}. ${dataPoint.month} → ${formatted} (${type}: $${value?.toLocaleString()})`);
});
