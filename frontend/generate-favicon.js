const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Caminho para o arquivo SVG de origem
const svgFile = path.join(__dirname, 'public', 'x-logo-improved.svg');

// Definir tamanhos para os diferentes favicons
const sizes = [16, 32, 48, 64, 128, 256];

// Crie uma pasta temporária para os PNGs
const tempDir = path.join(__dirname, 'temp_icons');
if (!fs.existsSync(tempDir)) {
  fs.mkdirSync(tempDir);
}

try {
  // Gerar PNGs de diferentes tamanhos
  sizes.forEach(size => {
    console.log(`Gerando PNG de ${size}x${size}...`);
    const outputPng = path.join(tempDir, `favicon-${size}.png`);
    
    // Usar o comando convert do ImageMagick com configurações melhoradas
    const cmd = `convert -background none -size ${size}x${size} ${svgFile} ${outputPng}`;
    execSync(cmd);
  });

  // Combine todos os PNGs em um único arquivo ICO
  console.log('Combinando PNGs em favicon.ico...');
  const outputIco = path.join(__dirname, 'public', 'favicon.ico');
  const pngFiles = sizes.map(size => path.join(tempDir, `favicon-${size}.png`)).join(' ');
  
  // O comando convert usando all pngs criados anteriormente
  const cmd = `convert ${pngFiles} ${outputIco}`;
  execSync(cmd);

  console.log('Favicon.ico foi criado com sucesso!');
} catch (error) {
  console.error('Erro ao gerar o favicon:', error);
} finally {
  // Limpar a pasta temporária
  if (fs.existsSync(tempDir)) {
    sizes.forEach(size => {
      const tempFile = path.join(tempDir, `favicon-${size}.png`);
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
      }
    });
    fs.rmdirSync(tempDir);
  }
}
