#include "DHT.h"

// --- MAPEAMENTO DE HARDWARE ---
#define PINO_DHT 2         // Fio de sinal do DHT11 conectado ao pino digital 2
#define TIPO_DHT DHT11     // Modelo do sensor de temperatura/umidade
#define PINO_LUZ_AO A0     // Pino AO do módulo MH-Sensor conectado ao Analógico 0
#define PINO_UMIDIFICADOR 3 // Pino S/IN do Módulo Relé conectado ao digital 3

DHT dht(PINO_DHT, TIPO_DHT);

// Variável para rastrear o status do relé e enviar para o backend
bool umidificadorLigado = false; 

void setup() {
  // Inicia a comunicação serial para enviar os dados ao PC/Raspberry
  Serial.begin(9600);
  
  // Aguarda a porta serial conectar (boa prática)
  while (!Serial) {
    ; 
  }

  Serial.println("Kampu - Inicializando Modulo de Sensoriamento e Controle (Clima + Luz + Umidificador)");
  
  dht.begin();
  
  // Configura a porta analógica como entrada de dados de luz
  pinMode(PINO_LUZ_AO, INPUT); 
  
  // Configura o pino do relé como saída de energia e garante que comece desligado
  pinMode(PINO_UMIDIFICADOR, OUTPUT);
  digitalWrite(PINO_UMIDIFICADOR, LOW);
}

void loop() {
  // O DHT11 precisa de pelo menos 2000 milissegundos (2 segundos) de estabilização entre leituras
  delay(2000);

  // --- COLETA DE DADOS ---
  float umidade = dht.readHumidity();
  float temperatura = dht.readTemperature();
  
  // Lê a tensão vinda do módulo LDR (0 a 1023)
  int luminosidade_crua = analogRead(PINO_LUZ_AO); 

  // --- VALIDAÇÃO ---
  // Se houver falha de comunicação com o DHT, loga o erro e pula este ciclo
  if (isnan(umidade) || isnan(temperatura)) {
    Serial.println("Erro_Hardware: Falha na leitura do DHT11");
    return;
  }

  // --- LÓGICA DE AUTOMAÇÃO (UMIDIFICADOR) ---
  // Se a umidade estiver abaixo de 50%, liga o relé
  if (umidade < 80.0) {
    digitalWrite(PINO_UMIDIFICADOR, HIGH); // Atraca o relé
    umidificadorLigado = true;
  } 
  // Se a umidade atingir ou passar de 65%, desliga o relé
  else if (umidade >= 87.0) {
    digitalWrite(PINO_UMIDIFICADOR, LOW);  // Solta o relé
    umidificadorLigado = false;
  }

  // --- TRANSMISSÃO (SERIALIZAÇÃO) ---
  // O formato usa o pipe '|' como delimitador para facilitar o split no Python
  Serial.print("U:");
  Serial.print(umidade);
  Serial.print("%|T:");
  Serial.print(temperatura);
  Serial.print("C|L:");
  Serial.print(luminosidade_crua); 
  
  // Adiciona o status do umidificador no final da string
  Serial.print("|H:");
  if (umidificadorLigado) {
    Serial.println("ON");
  } else {
    Serial.println("OFF");
  }
}