#!/usr/bin/env node

// Teste rápido da lógica de decisão de team costs
// Simula diferentes cenários para verificar a lógica

const scenarios = [
  {
    name: "Sem credenciais",
    hasCredentials: false,
    teamCostsError: null,
    apiTeamCostsData: undefined
  },
  {
    name: "Com credenciais, API sucesso, com dados",
    hasCredentials: true,
    teamCostsError: null,
    apiTeamCostsData: { data: [{ team_name: "Dev", total_cost: 1000 }] }
  },
  {
    name: "Com credenciais, API sucesso, sem dados",
    hasCredentials: true,
    teamCostsError: null,
    apiTeamCostsData: { data: [] }
  },
  {
    name: "Com credenciais, API com erro",
    hasCredentials: true,
    teamCostsError: new Error("API Error"),
    apiTeamCostsData: undefined
  }
];

scenarios.forEach(scenario => {
  const shouldUseRealTeamCosts = scenario.hasCredentials && !scenario.teamCostsError && scenario.apiTeamCostsData?.data !== undefined;
  
  console.log(`\n📋 ${scenario.name}:`);
  console.log(`   shouldUseRealTeamCosts: ${shouldUseRealTeamCosts}`);
  console.log(`   Resultado: ${shouldUseRealTeamCosts ? 'Usa dados reais' : 'Usa mock data'}`);
  
  if (shouldUseRealTeamCosts && scenario.apiTeamCostsData.data.length === 0) {
    console.log(`   🎯 Mostrará: Mensagem "sem dados"`);
  } else if (shouldUseRealTeamCosts) {
    console.log(`   🎯 Mostrará: Gráfico com ${scenario.apiTeamCostsData.data.length} equipe(s)`);
  } else {
    console.log(`   🎯 Mostrará: Dados mockados`);
  }
});
