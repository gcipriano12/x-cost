#!/usr/bin/env node

// Teste para simular o comportamento com 100 equipes

const generateMockTeams = (count) => {
  const teams = [];
  const teamNames = [
    'Desenvolvimento', 'Infraestrutura', 'DevOps', 'QA', 'Product', 'Design', 
    'Marketing', 'Sales', 'Support', 'Data Science', 'Security', 'Mobile',
    'Frontend', 'Backend', 'Platform', 'Analytics', 'Research', 'Operations'
  ];
  
  for (let i = 0; i < count; i++) {
    const baseName = teamNames[i % teamNames.length];
    const suffix = Math.floor(i / teamNames.length) + 1;
    const name = suffix > 1 ? `${baseName} ${suffix}` : baseName;
    
    // Simular distribuição realística de custos (algumas equipes gastam muito mais)
    const baseValue = Math.random() * 50000;
    const multiplier = i < 5 ? 10 : i < 15 ? 5 : 1; // Top 5 gastam 10x mais, próximas 10 gastam 5x mais
    
    teams.push({
      name,
      value: Math.round(baseValue * multiplier),
      color: `#${Math.floor(Math.random()*16777215).toString(16)}`
    });
  }
  
  return teams.sort((a, b) => b.value - a.value); // Ordenar por valor
};

// Simular o processamento que agora está no componente
const processTeamsData = (teams, maxTeamsToShow = 15) => {
  if (teams.length <= maxTeamsToShow) {
    return { displayData: teams, hiddenTeamsCount: 0, hiddenTeamsValue: 0 };
  }

  const sortedTeams = [...teams].sort((a, b) => b.value - a.value);
  const topTeams = sortedTeams.slice(0, maxTeamsToShow - 1);
  const hiddenTeams = sortedTeams.slice(maxTeamsToShow - 1);
  
  const hiddenTeamsValue = hiddenTeams.reduce((sum, team) => sum + team.value, 0);
  const hiddenTeamsCount = hiddenTeams.length;

  const othersItem = {
    name: `Outros (${hiddenTeamsCount})`,
    value: hiddenTeamsValue,
    color: '#6B7280'
  };

  return {
    displayData: [...topTeams, othersItem],
    hiddenTeamsCount,
    hiddenTeamsValue
  };
};

// Testar diferentes cenários
const scenarios = [
  { count: 5, desc: "5 equipes (normal)" },
  { count: 15, desc: "15 equipes (limite)" },
  { count: 25, desc: "25 equipes (com agrupamento)" },
  { count: 100, desc: "100 equipes (muitas equipes)" }
];

scenarios.forEach(scenario => {
  console.log(`\n📊 ${scenario.desc}:`);
  
  const mockTeams = generateMockTeams(scenario.count);
  const processed = processTeamsData(mockTeams);
  
  console.log(`   📈 Total de equipes: ${scenario.count}`);
  console.log(`   👁️  Equipes visíveis: ${processed.displayData.length}`);
  console.log(`   🫥 Equipes ocultas: ${processed.hiddenTeamsCount}`);
  
  if (processed.hiddenTeamsCount > 0) {
    const totalValue = mockTeams.reduce((sum, t) => sum + t.value, 0);
    const visibleValue = processed.displayData.reduce((sum, t) => sum + t.value, 0) - processed.hiddenTeamsValue;
    const hiddenPercentage = ((processed.hiddenTeamsValue / totalValue) * 100).toFixed(1);
    
    console.log(`   💰 Valor das ocultas: $${processed.hiddenTeamsValue.toLocaleString()} (${hiddenPercentage}%)`);
  }
  
  // Simular altura do gráfico
  const minHeight = 320;
  const maxHeight = 600;
  const itemHeight = 35;
  const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, processed.displayData.length * itemHeight + 100));
  
  console.log(`   📏 Altura do gráfico: ${calculatedHeight}px`);
  
  // Mostrar top 5 equipes
  console.log(`   🏆 Top 5 equipes:`);
  processed.displayData.slice(0, 5).forEach((team, i) => {
    console.log(`       ${i+1}. ${team.name}: $${team.value.toLocaleString()}`);
  });
});

console.log('\n✅ Resumo das melhorias implementadas:');
console.log('   • Limitação a 15 equipes visíveis (configurável)');
console.log('   • Agrupamento de equipes menores em "Outros"');
console.log('   • Altura dinâmica do gráfico (320px - 600px)');
console.log('   • Barras adaptativas (20px - 30px)');
console.log('   • YAxis mais largo para nomes longos');
console.log('   • Informação sobre equipes ocultas');
