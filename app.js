const express = require('express');
const axios = require('axios');
const sql = require('mssql');
const app = express();
const port = process.env.PORT || 3000;

// Configuração da conexão com SQL Server
const dbConfig = {
  user: 'sa',
  password: 'L@gtech1100',
  server: '192.168.30.16', // Endereço do servidor
  database: 'EXPERTOS',
  options: {
    encrypt: true, // Caso esteja usando o SQL Server com criptografia
    trustServerCertificate: true // Alterar para 'false' em ambientes de produção
  }
};

// Função para conectar ao banco de dados
const getDbConnection = async () => {
  try {
    const pool = await sql.connect(dbConfig);
    return pool;
  } catch (err) {
    console.error("Erro ao conectar ao banco de dados: ", err);
    return null;
  }
};

// Rota para buscar dados do SQL Server
app.get('/dados', async (req, res) => {
  try {
    const pool = await getDbConnection();
    if (!pool) {
      return res.status(500).json({ erro: "Falha ao conectar ao banco de dados" });
    }

    const result = await pool.request().query('SELECT TOP 10 * FROM usuario');
    res.json(result.recordset); // Retorna os dados no formato JSON
  } catch (err) {
    console.error("Erro ao buscar dados: ", err);
    res.status(500).json({ erro: err.message });
  }
});

// Rota para consumir a API hospedada no Render
app.get('/api-remota', async (req, res) => {
  try {
    const url = "https://api-expert-os.onrender.com/dados";  // Substitua se necessário
    const response = await axios.get(url, { timeout: 15000 });  // Aumenta o tempo de espera
    
    if (response.status === 200) {
      return res.json(response.data);  // Retorna os dados da API externa
    } else {
      console.error(`Erro ao conectar na API externa: ${response.status}`);
      return res.status(500).json({ erro: "Falha ao conectar na API externa", status_code: response.status });
    }
  } catch (err) {
    console.error("Erro ao acessar API externa: ", err);
    res.status(500).json({ erro: err.message });
  }
});

// Função para pingar a API e evitar que hiberne no Render
const keepAwake = async () => {
  const url = "https://api-expert-os.onrender.com/dados"; // Substitua pela URL da sua API
  setInterval(async () => {
    try {
      const response = await axios.get(url);
      console.log(`Ping enviado! Status: ${response.status}`);
    } catch (err) {
      console.error("Erro ao pingar API: ", err);
    }
  }, 600000);  // Pingar a cada 10 minutos
};

// Iniciar o ping automático
keepAwake();

// Iniciar o servidor
app.listen(port, () => {
  console.log(`Servidor rodando na porta ${port}`);
});
