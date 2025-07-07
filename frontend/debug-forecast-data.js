/**
 * Script para debugar dados do forecast e ordem das datas
 */

// Simular dados que podem estar vindo da API
const sampleApiData = [
  { month: 'Jan', actual: 280000, budget: 350000 },
  { month: 'Feb', actual: 320000, budget: 350000 },
  { month: 'Mar', actual: 290000, budget: 350000 },
  { month: 'Apr', actual: 310000, budget: 350000 },
  { month: 'May', actual: 340000, budget: 350000 },
  { month: 'Jun', actual: 330000, budget: 350000 },
  { month: 'Jul', actual: 345000, budget: 350000 },
  { month: 'Aug', forecast: 355000, budget: 350000 },
  { month: 'Sep', forecast: 360000, budget: 350000 },
  { month: 'Oct', forecast: 365000, budget: 350000 },
  { month: 'Nov', forecast: 370000, budget: 350000 },
  { month: 'Dec', forecast: 375000, budget: 350000 }
];

// Função original que estava causando problemas
const formatMonthWithYearOriginal = (monthStr, data, currentMonth = 7, currentYear = 2025) => {
  if (!monthStr) return monthStr;
  
  // Se já contém ano, retorna como está
  if (monthStr.includes('/')) return monthStr;
  
  // Mapear meses abreviados para números
  const monthMap = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
  };
  
  const monthNum = monthMap[monthStr];
  if (!monthNum) return monthStr;
  
  // Encontrar o índice do mês atual nos dados para contextualizar
  const currentIndex = data.findIndex(d => d.month === monthStr);
  if (currentIndex === -1) return monthStr;
  
  let year = currentYear;
  
  // Se é um dos primeiros meses nos dados e é posterior ao mês atual,
  // provavelmente é do ano passado
  if (currentIndex < data.length / 2 && monthNum > currentMonth) {
    year = currentYear - 1; // 2024
  }
  // Se é um dos últimos meses nos dados e é anterior ao mês atual,
  // provavelmente é do próximo ano (forecast)
  else if (currentIndex >= data.length / 2 && monthNum < currentMonth) {
    year = currentYear + 1; // 2026
  }
  
  // Ajuste especial: se é dados históricos (tem actual) e está no final da lista
  // mas o mês é posterior ao atual, deve ser do ano passado
  const currentDataPoint = data[currentIndex];
  if (currentDataPoint?.actual !== undefined && monthNum > currentMonth) {
    year = currentYear - 1; // 2024
  }
  
  // Ajuste especial: se é forecast (só tem forecast) e o mês já passou
  if (currentDataPoint?.forecast !== undefined && currentDataPoint?.actual === undefined && monthNum < currentMonth) {
    year = currentYear + 1; // 2026
  }
  
  // Retornar formato curto (YY)
  const shortYear = year.toString().slice(-2);
  return `${monthStr}/${shortYear}`;
};

// Nova função corrigida
const formatMonthWithYearNew = (monthStr, data, currentMonth = 7, currentYear = 2025) => {
  if (!monthStr) return monthStr;
  
  // Se já contém ano, retorna como está
  if (monthStr.includes('/')) return monthStr;
  
  // Mapear meses abreviados para números
  const monthMap = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
  };
  
  const monthNum = monthMap[monthStr];
  if (!monthNum) return monthStr;
  
  const currentIndex = data.findIndex(d => d.month === monthStr);
  if (currentIndex === -1) return monthStr;
  
  // Lógica mais simples e robusta:
  // 1. Se o mês é <= mês atual E tem dados actual, é ano atual ou passado
  // 2. Se o mês é > mês atual E tem dados actual, é ano passado
  // 3. Se só tem forecast, determinar baseado na posição na sequência
  
  const currentDataPoint = data[currentIndex];
  let year = currentYear;
  
  if (currentDataPoint?.actual !== undefined) {
    // Dados históricos reais
    if (monthNum > currentMonth) {
      year = currentYear - 1; // Ano passado
    } else {
      year = currentYear; // Ano atual
    }
  } else if (currentDataPoint?.forecast !== undefined) {
    // Dados de previsão
    if (monthNum < currentMonth) {
      year = currentYear + 1; // Próximo ano
    } else {
      year = currentYear; // Ano atual
    }
  }
  
  const shortYear = year.toString().slice(-2);
  return `${monthStr}/${shortYear}`;
};

console.log('=== TESTE FUNÇÃO ORIGINAL ===');
sampleApiData.forEach(point => {
  const formatted = formatMonthWithYearOriginal(point.month, sampleApiData);
  const type = point.actual ? 'actual' : 'forecast';
  console.log(`${point.month} -> ${formatted} (${type})`);
});

console.log('\n=== TESTE FUNÇÃO NOVA ===');
sampleApiData.forEach(point => {
  const formatted = formatMonthWithYearNew(point.month, sampleApiData);
  const type = point.actual ? 'actual' : 'forecast';
  console.log(`${point.month} -> ${formatted} (${type})`);
});

// Teste específico do cenário problemático
console.log('\n=== TESTE CENÁRIO ESPECÍFICO ===');
const problematicData = [
  { month: 'Aug', actual: 100000 },
  { month: 'Sep', actual: 110000 },
  { month: 'Oct', actual: 120000 },
  { month: 'Nov', actual: 130000 },
  { month: 'Dec', actual: 140000 },
  { month: 'Jan', actual: 150000 },
  { month: 'Feb', actual: 160000 },
  { month: 'Mar', actual: 170000 },
  { month: 'Apr', actual: 180000 },
  { month: 'May', actual: 190000 },
  { month: 'Jun', actual: 200000 },
  { month: 'Jul', forecast: 210000 },
];

console.log('Original:');
problematicData.forEach(point => {
  const formatted = formatMonthWithYearOriginal(point.month, problematicData);
  console.log(`${point.month} -> ${formatted}`);
});

console.log('\nNova:');
problematicData.forEach(point => {
  const formatted = formatMonthWithYearNew(point.month, problematicData);
  console.log(`${point.month} -> ${formatted}`);
});
