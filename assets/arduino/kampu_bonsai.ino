#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>
#include <ArduinoOTA.h>
#include <ESP8266HTTPUpdateServer.h>
#include <time.h>
#include <EEPROM.h>
#include <Dusk2Dawn.h>

ESP8266WebServer server(80);
ESP8266HTTPUpdateServer httpUpdater;

const int relePin = 5; 
const long fusoHorario = -3 * 3600; 
const int horarioVerao = 0; 

int ultimoMinuto = -1; 
int estadoAutomaticoAnterior = -1; // -1 significa "acabou de dar boot, estado desconhecido"

float lat;
float lon;

String logTerminal = "Kampu OS - Aguardando NTP...\n";

void printLog(String mensagem) {
  time_t agora = time(nullptr);
  struct tm* infoTempo = localtime(&agora);
  char buf[15];
  sprintf(buf, "%02d:%02d:%02d ", infoTempo->tm_hour, infoTempo->tm_min, infoTempo->tm_sec);
  
  String linha = String(buf) + "- " + mensagem + "\n";
  Serial.print(linha); 
  logTerminal += linha; 
  
  if (logTerminal.length() > 2000) {
    logTerminal = logTerminal.substring(logTerminal.length() - 1000); 
  }
}

void setup() {
  Serial.begin(115200);
  
  EEPROM.begin(512);
  EEPROM.get(0, lat);
  EEPROM.get(sizeof(float), lon);

  if (isnan(lat) || isnan(lon) || lat < -90.0 || lat > 90.0 || lon < -180.0 || lon > 180.0) {
    lat = -9.6658;
    lon = -35.7353;
    EEPROM.put(0, lat);
    EEPROM.put(sizeof(float), lon);
    EEPROM.commit();
  }

  pinMode(relePin, OUTPUT);
  digitalWrite(relePin, LOW); // Assume desligado até o NTP dizer o contrário

  WiFiManager wifiManager;
  if (!wifiManager.autoConnect("Kampu-Setup")) {
    delay(3000);
    ESP.restart();
  }

  ArduinoOTA.setHostname("Kampu-Core"); 
  ArduinoOTA.begin(); 
  httpUpdater.setup(&server, "/update");
  
  configTime(fusoHorario, horarioVerao, "pool.ntp.org", "time.nist.gov");

  server.on("/", []() {
    String html = "<html><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
    html += "<style>body { font-family: sans-serif; text-align: center; margin-top: 20px; background-color:#f4f4f9; } ";
    html += ".btn { display: block; width: 250px; margin: 15px auto; padding: 15px; font-size: 20px; font-weight: bold; text-decoration: none; color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); } ";
    html += ".on { background-color: #2e7d32; } .off { background-color: #c62828; } .ota { background-color: #0277bd; font-size: 16px;} ";
    html += "#terminal { background-color: #1e1e1e; color: #4af626; text-align: left; padding: 10px; margin: 20px auto; width: 90%; max-width: 400px; height: 200px; overflow-y: scroll; font-family: monospace; border-radius: 5px; border: 1px solid #333; font-size: 14px; white-space: pre-wrap;}";
    html += ".card { background:#fff; padding:15px; border-radius:8px; width:90%; max-width:300px; margin: 10px auto; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }</style></head><body>";
    
    html += "<h1 style=\"color:#333; margin-bottom: 5px;\">Kampu</h1>";
    html += "<h2 id=\"relogio\" style=\"color:#555; margin-top: 0;\">--:--:--</h2>"; 
    
    html += "<div class=\"card\">";
    html += "<h3 style=\"margin-top:0; color:#555; font-size:16px;\">Ciclo Solar</h3>";
    html += "<p id=\"sol_status\" style=\"font-size: 16px; font-weight: bold; color: #d84315; margin-top:-5px;\">Sincronizando...</p>";
    
    html += "<form action=\"/config\" method=\"GET\" style=\"margin-bottom: 0;\">";
    html += "<label style=\"font-size:12px; color:#666;\">Latitude</label> &nbsp; ";
    html += "<label style=\"font-size:12px; color:#666; margin-left:15px;\">Longitude</label><br>";
    html += "<input type=\"text\" name=\"lat\" value=\"" + String(lat, 4) + "\" style=\"width:80px; text-align:center; margin-bottom:10px;\"> &nbsp; ";
    html += "<input type=\"text\" name=\"lon\" value=\"" + String(lon, 4) + "\" style=\"width:80px; text-align:center; margin-bottom:10px;\"><br>";
    html += "<input type=\"submit\" value=\"ATUALIZAR COORDENADAS\" style=\"background:#333; color:#fff; border:none; padding:8px; width:100%; border-radius:5px; font-weight:bold; cursor:pointer;\">";
    html += "</form></div>";
    
    html += "<a href=\"/ligar\" class=\"btn on\">LIGAR PAINEL</a>";
    html += "<a href=\"/desligar\" class=\"btn off\">DESLIGAR PAINEL</a>";
    html += "<a href=\"/update\" class=\"btn ota\">ATUALIZAR SISTEMA (OTA)</a>";
    
    html += "<div id=\"terminal\">Carregando logs...</div>"; 
    
    html += "<script>setInterval(function(){ ";
    html += "fetch('/console').then(r => r.text()).then(t => { const term = document.getElementById('terminal'); const isScrolled = term.scrollHeight - term.clientHeight <= term.scrollTop + 1; term.innerHTML = t; if(isScrolled) term.scrollTop = term.scrollHeight; }); ";
    html += "fetch('/dados').then(r => r.json()).then(d => { document.getElementById('relogio').innerText = d.hora; document.getElementById('sol_status').innerHTML = '☀️ Nascer: ' + d.nascer + ' &nbsp; | &nbsp; 🌙 Pôr: ' + d.por; }); ";
    html += "}, 1000);</script>";
    
    html += "</body></html>";
    server.send(200, "text/html", html);
  });

  server.on("/config", []() {
    if (server.hasArg("lat") && server.hasArg("lon")) {
      lat = server.arg("lat").toFloat();
      lon = server.arg("lon").toFloat();
      EEPROM.put(0, lat);
      EEPROM.put(sizeof(float), lon);
      EEPROM.commit();
      
      // Força o recálculo do estado automático no próximo minuto
      estadoAutomaticoAnterior = -1; 
      
      printLog("Coordenadas atualizadas (Lat: " + String(lat, 4) + " Lon: " + String(lon, 4) + ")");
    }
    server.sendHeader("Location","/");
    server.send(303);
  });

  server.on("/dados", []() {
    time_t agora = time(nullptr);
    struct tm* infoTempo = localtime(&agora);
    
    String json = "{";
    if (infoTempo->tm_year > 120) {
        char buf[15];
        sprintf(buf, "%02d:%02d:%02d", infoTempo->tm_hour, infoTempo->tm_min, infoTempo->tm_sec);
        json += "\"hora\":\"" + String(buf) + "\",";
        
        Dusk2Dawn sol(lat, lon, fusoHorario / 3600);
        int sr = sol.sunrise(infoTempo->tm_year + 1900, infoTempo->tm_mon + 1, infoTempo->tm_mday, horarioVerao);
        int ss = sol.sunset(infoTempo->tm_year + 1900, infoTempo->tm_mon + 1, infoTempo->tm_mday, horarioVerao);
        
        char srBuf[10], ssBuf[10];
        sprintf(srBuf, "%02d:%02d", sr / 60, sr % 60);
        sprintf(ssBuf, "%02d:%02d", ss / 60, ss % 60);
        
        json += "\"nascer\":\"" + String(srBuf) + "\",";
        json += "\"por\":\"" + String(ssBuf) + "\"";
    } else {
        json += "\"hora\":\"Sincronizando...\",\"nascer\":\"--:--\",\"por\":\"--:--\"";
    }
    json += "}";
    server.send(200, "application/json", json);
  });

  server.on("/console", []() { server.send(200, "text/plain", logTerminal); });

  server.on("/ligar", []() { 
    digitalWrite(relePin, HIGH); 
    estadoAutomaticoAnterior = HIGH; // Atualiza a variável para a automação não brigar com o usuário
    printLog("Comando WEB: Rele atracado (ON)");
    server.sendHeader("Location","/"); 
    server.send(303); 
  });
  
  server.on("/desligar", []() { 
    digitalWrite(relePin, LOW); 
    estadoAutomaticoAnterior = LOW; // Atualiza a variável para a automação não brigar com o usuário
    printLog("Comando WEB: Rele liberado (OFF)");
    server.sendHeader("Location","/"); 
    server.send(303); 
  });

  server.begin();
  printLog("Kampu Core Inicializado e na Rede.");
}

void loop() {
  ArduinoOTA.handle(); 
  server.handleClient();

  time_t agora = time(nullptr);
  struct tm* infoTempo = localtime(&agora);

  if (infoTempo->tm_year > 120 && infoTempo->tm_min != ultimoMinuto) { 
    ultimoMinuto = infoTempo->tm_min;

    Dusk2Dawn sol(lat, lon, fusoHorario / 3600);
    int minutoNascer = sol.sunrise(infoTempo->tm_year + 1900, infoTempo->tm_mon + 1, infoTempo->tm_mday, horarioVerao);
    int minutoPor    = sol.sunset(infoTempo->tm_year + 1900, infoTempo->tm_mon + 1, infoTempo->tm_mday, horarioVerao);
    
    int minutosHoje = (infoTempo->tm_hour * 60) + infoTempo->tm_min;

    // Define qual o estado natural que o painel deveria ter neste momento
    int estadoEsperado = (minutosHoje >= minutoNascer && minutosHoje < minutoPor) ? HIGH : LOW;

    // Só atua no hardware se o estado natural mudou (transição dia/noite) 
    // OU se a placa acabou de ligar/sincronizar (-1)
    if (estadoEsperado != estadoAutomaticoAnterior) {
      digitalWrite(relePin, estadoEsperado);
      estadoAutomaticoAnterior = estadoEsperado;
      
      if (estadoEsperado == HIGH) {
        printLog("Auto-Sync: Quantum Board LIGADA (Período Diurno)");
      } else {
        printLog("Auto-Sync: Quantum Board DESLIGADA (Período Noturno)");
      }
    }
  }
}