#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WebServer.h>
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

#define RELAY_ON HIGH
#define RELAY_OFF LOW

// --- Servidor Web para comandos manuais ---
ESP8266WebServer server(80);

unsigned long ultimoEnvio = 0;
const long intervalo = 10000; // Envio a cada 10 segundos

// Variável para rastrear o status e enviar ao Flask
String statusUmidificador = "OFF";

// Controle manual: quando true, o loop automático de umidade NÃO mexe no relé
bool modoManual = false;

void ligarRele() {
  digitalWrite(RELAY_PIN, RELAY_ON);
  statusUmidificador = "ON";
}

void desligarRele() {
  digitalWrite(RELAY_PIN, RELAY_OFF);
  statusUmidificador = "OFF";
}

// --- Handlers HTTP ---
void handleReleOn() {
  modoManual = true;
  ligarRele();
  server.send(200, "application/json", "{\"status\":\"ON\",\"modo\":\"manual\"}");
  Serial.println("[HTTP] Rele ligado manualmente");
}

void handleReleOff() {
  modoManual = true;
  desligarRele();
  server.send(200, "application/json", "{\"status\":\"OFF\",\"modo\":\"manual\"}");
  Serial.println("[HTTP] Rele desligado manualmente");
}

void handleReleAuto() {
  modoManual = false;
  server.send(200, "application/json", "{\"modo\":\"automatico\"}");
  Serial.println("[HTTP] Voltou para modo automatico");
}

void handleStatus() {
  StaticJsonDocument<200> doc;
  doc["rele"] = statusUmidificador;
  doc["modo"] = modoManual ? "manual" : "automatico";
  doc["umidade"] = dht.readHumidity();
  doc["temperatura"] = dht.readTemperature();

  String resposta;
  serializeJson(doc, resposta);
  server.send(200, "application/json", resposta);
}

void setup() {
  Serial.begin(115200);
  // Garante que o relé comece desligado ANTES de abrir a porta
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, RELAY_OFF);

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
    Serial.print("IP do dispositivo: ");
    Serial.println(WiFi.localIP());

    // --- Registra as rotas do servidor web ---
    server.on("/rele/on", handleReleOn);
    server.on("/rele/off", handleReleOff);
    server.on("/rele/auto", handleReleAuto);
    server.on("/status", handleStatus);
    server.begin();
    Serial.println("Servidor HTTP iniciado.");
    Serial.println("Endpoints: /rele/on  /rele/off  /rele/auto  /status");
  } else {
    Serial.println("\nFalha no Wi-Fi. Iniciando modo offline (Apenas controle local do relé).");
  }
}

void loop() {
  // Atende requisições HTTP a cada iteração do loop
  server.handleClient();

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
    // Só roda automaticamente se NÃO estiver em modo manual
    if (!modoManual) {
      // Se a umidade cair abaixo de 70%, liga o atomizador
      if (umidade < 70.0) {
        ligarRele();
      }
      // Se a umidade chegar a 85% ou mais, desliga o atomizador
      else if (umidade >= 85.0) {
        desligarRele();
      }
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
      doc["modo"] = modoManual ? "manual" : "automatico";

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