const char LINE_SEP = '\n';
const char PARAM_SEP = ';';
const char SERVER_PREFIX = 's';


void setup() {
  Serial.begin(9600);
  Serial.println("Setting up.");
}

void loop() {
  String line = readline();
  Serial.print("Received line : ");
  Serial.println(line);
}

String readline() {
  while (Serial.available() < 2){}
    // wait for serial to be avaiable.
  
  String buf = "";
  char prefix[2] = {};
  Serial.readBytes(prefix, 2);
  Serial.print("Is this a server prefix? ");
  Serial.println(prefix);
  buf += prefix;

  char current = 'c';
  while (current != LINE_SEP) {
    current = Serial.read();
    buf += current;
    if (prefix[0] == SERVER_PREFIX && prefix[1] == PARAM_SEP) {
      Serial.print("Reading server data > ");
    }
    else {
      Serial.print("Receiveing non-server bytes : ");
    }
    Serial.println(current);
  }
  if (current == LINE_SEP)  {
    Serial.print("c;Client Received > ");
    Serial.println(buf);
    return buf;
  }
}

void echo() {
  String line = readline();
  Serial.print(line);
}

void send_parsable_line() {
  Serial.println("\"text\";false;true;10;10.3;[\"1\",2]");
}

void receive_parse_line()  {
  String line = Serial.readStringUntil(LINE_SEP);
  line.trim();
  Serial.println("[Received] : " + line);

  char* ptr;
  ptr = strtok(line.c_str(), PARAM_SEP);
  while (ptr != NULL)  {
    Serial.println(ptr);
    ptr = strtok(NULL, PARAM_SEP);
  }
}

void parse_test() {
  send_parsable_line();
  receive_parse_line();
}
