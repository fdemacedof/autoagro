#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// O compilador vai substituir automaticamente pelos valores do platformio.ini
const char* ssid = WIFI_SSID;
const char* password = WIFI_PASS;

// --- URL do Backend Flask ---
const char* serverUrl = "http://192.168.0.40:5000/api/sensores"; 

// --- Configurações do Sensor DHT11 ---
#define DHTPIN D2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// --- Configuração do Relé (Umidificador) ---
#define RELAY_PIN D1
// A maioria dos módulos de relé acionam em nível BAIXO (LOW = Liga, HIGH = Desliga)
#define RELAY_ON LOW
#define RELAY_OFF HIGH

unsigned long ultimoEnvio = 0;
const long intervalo = 10000; // Envio a cada 10 segundos

// Variável para rastrear o status e enviar ao Flask
String statusUmidificador = "OFF";

void setup() {
  Serial.begin(115200);
  
  // Garante que o relé comece desligado ANTES de abrir a porta
  digitalWrite(RELAY_PIN, RELAY_OFF);
  pinMode(RELAY_PIN, OUTPUT);

  dht.begin();

  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  // Tenta conectar por no máximo 10 segundos (20 tentativas de 500ms)
  int tentativas = 0;
  while (WiFi.status() != WL_CONNECTED && tentativas < 20) {
    delay(500);
    Serial.print(".");
    tentativas++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi conectado!");
  } else {
    Serial.println("\nFalha no Wi-Fi. Iniciando modo offline (Apenas controle local do relé).");
  }
}

void loop() {
  unsigned long tempoAtual = millis();

  if (tempoAtual - ultimoEnvio >= intervalo) {
    ultimoEnvio = tempoAtual;

    float umidade = dht.readHumidity();
    float temperatura = dht.readTemperature();

    if (isnan(umidade) || isnan(temperatura)) {
      Serial.println("Falha ao ler o sensor DHT11!");
      return;
    }

    // ==========================================
    // LÓGICA DE CONTROLE DO UMIDIFICADOR
    // ==========================================
    // Se a umidade cair abaixo de 80%, liga o atomizador
    if (umidade < 80.0) {
      digitalWrite(RELAY_PIN, RELAY_ON);
      statusUmidificador = "ON";
    } 
    // Se a umidade chegar a 85% ou mais, desliga o atomizador
    else if (umidade >= 85.0) {
      digitalWrite(RELAY_PIN, RELAY_OFF);
      statusUmidificador = "OFF";
    }

    // ==========================================
    // ENVIO DOS DADOS PARA O FLASK
    // ==========================================
    if (WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;

      http.begin(client, serverUrl);
      http.addHeader("Content-Type", "application/json");

      // Montando o payload JSON (Usando a versão 6 do ArduinoJson baseada no seu platformio.ini)
      StaticJsonDocument<200> doc;
      doc["dispositivo_id"] = "esp8266_node_01";
      doc["temperatura_ar"] = temperatura;
      doc["umidade_ar"] = umidade;
      doc["umidificador"] = statusUmidificador; // Envia o estado real da máquina

      String requestBody;
      serializeJson(doc, requestBody);
      
      int httpResponseCode = http.POST(requestBody);

      if (httpResponseCode > 0) {
        Serial.print("Enviado: ");
        Serial.println(requestBody);
      } else {
        Serial.print("Erro HTTP: ");
        Serial.println(httpResponseCode);
      }

      http.end(); 
    }
  }
}