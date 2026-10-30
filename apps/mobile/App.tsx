import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  API_BASE_URL,
  ApiRequestError,
  api,
  type AssistantResponse,
  type Election,
  type Envelope,
  type FeatureCollection,
  type Health,
  type Observation,
  type Prediction,
  type Scenario,
  type Territory,
} from "./src/api";

type TabId = "inicio" | "datos" | "mapa" | "prediccion" | "escenarios" | "ayuda";
type LoadState = "loading" | "ready" | "empty" | "error";

const tabs: Array<{ id: TabId; label: string }> = [
  { id: "inicio", label: "Inicio" },
  { id: "datos", label: "Datos" },
  { id: "mapa", label: "Mapa" },
  { id: "prediccion", label: "Predicción" },
  { id: "escenarios", label: "Escenarios" },
  { id: "ayuda", label: "Ayuda" },
];

function formatPct(value: number | undefined): string {
  return value === undefined ? "Sin datos" : `${value.toFixed(1)}%`;
}

function messageFor(error: unknown): string {
  if (error instanceof ApiRequestError && error.status === 0) return "Sin conexión. Revisa la URL de API y la red local.";
  if (error instanceof ApiRequestError) return error.message;
  if (error instanceof Error) return error.message;
  return "No se pudo completar la solicitud.";
}

function App() {
  const [tab, setTab] = useState<TabId>("inicio");
  const [catalogState, setCatalogState] = useState<LoadState>("loading");
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [catalogAttempt, setCatalogAttempt] = useState(0);
  const [health, setHealth] = useState<Envelope<Health> | null>(null);
  const [territories, setTerritories] = useState<Territory[]>([]);
  const [elections, setElections] = useState<Election[]>([]);
  const [territoryId, setTerritoryId] = useState("");
  const [electionId, setElectionId] = useState("");
  const [detailState, setDetailState] = useState<LoadState>("loading");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [detailAttempt, setDetailAttempt] = useState(0);
  const [history, setHistory] = useState<Envelope<Observation[]> | null>(null);
  const [prediction, setPrediction] = useState<Envelope<Prediction> | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);
  const [map, setMap] = useState<Envelope<FeatureCollection> | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);
  const [scenario, setScenario] = useState<Envelope<Scenario> | null>(null);
  const [scenarioState, setScenarioState] = useState<LoadState>("ready");
  const [scenarioError, setScenarioError] = useState<string | null>(null);
  const [question, setQuestion] = useState("¿Qué representa la tasa?");
  const [assistant, setAssistant] = useState<Envelope<AssistantResponse> | null>(null);
  const [assistantState, setAssistantState] = useState<LoadState>("ready");
  const [assistantError, setAssistantError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setCatalogState("loading");
    setCatalogError(null);
    Promise.all([api.getHealth(), api.getTerritories(), api.getElections()])
      .then(([healthResponse, territoryResponse, electionResponse]) => {
        if (!active) return;
        setHealth(healthResponse);
        setTerritories(territoryResponse.data);
        setElections(electionResponse.data);
        setTerritoryId((current) => current || territoryResponse.data[0]?.id || "");
        setElectionId((current) => current || electionResponse.data[electionResponse.data.length - 1]?.election_id || "");
        setCatalogState(territoryResponse.data.length && electionResponse.data.length ? "ready" : "empty");
      })
      .catch((error: unknown) => {
        if (!active) return;
        setCatalogState("error");
        setCatalogError(messageFor(error));
      });
    return () => {
      active = false;
    };
  }, [catalogAttempt]);

  useEffect(() => {
    if (!territoryId) return;
    let active = true;
    setDetailState("loading");
    setDetailError(null);
    setPredictionError(null);
    setMapError(null);
    setHistory(null);
    setPrediction(null);
    setMap(null);
    const mapRequest = tab === "mapa" ? api.getMap(territoryId) : Promise.resolve(null);
    Promise.allSettled([api.getParticipation(territoryId), api.getPrediction(territoryId), mapRequest]).then(
      ([historyResult, predictionResult, mapResult]) => {
        if (!active) return;
        if (historyResult.status === "fulfilled") {
          setHistory(historyResult.value);
          setDetailState(historyResult.value.data.length ? "ready" : "empty");
        } else {
          setDetailState("error");
          setDetailError(messageFor(historyResult.reason));
        }
        if (predictionResult.status === "fulfilled") setPrediction(predictionResult.value);
        else setPredictionError(messageFor(predictionResult.reason));
        if (mapResult.status === "fulfilled" && mapResult.value) setMap(mapResult.value);
        else if (mapResult.status === "rejected") setMapError(messageFor(mapResult.reason));
      },
    );
    return () => {
      active = false;
    };
  }, [territoryId, tab, detailAttempt]);

  const territory = territories.find((item) => item.id === territoryId);
  const selectedObservation = history?.data.find((item) => item.election_id === electionId) || history?.data[history.data.length - 1];
  const sourceVersion = history?.meta.source_version || health?.meta.source_version || "Sin version";

  async function calculateScenario(deltaPp: number) {
    if (!territoryId) return;
    setScenarioState("loading");
    setScenarioError(null);
    try {
      setScenario(await api.getScenario(territoryId, deltaPp));
      setScenarioState("ready");
    } catch (error) {
      setScenario(null);
      setScenarioState("error");
      setScenarioError(messageFor(error));
    }
  }

  async function askAssistant() {
    if (!territoryId || !question.trim()) return;
    setAssistantState("loading");
    setAssistantError(null);
    try {
      setAssistant(await api.askAssistant(territoryId, question.trim()));
      setAssistantState("ready");
    } catch (error) {
      setAssistant(null);
      setAssistantState("error");
      setAssistantError(messageFor(error));
    }
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.screen} keyboardShouldPersistTaps="handled">
        <View style={styles.header}>
          <View>
            <Text style={styles.kicker}>CIVIA</Text>
            <Text style={styles.title}>Datos para comprender</Text>
          </View>
          <View style={[styles.statusPill, health?.data.status === "ok" ? styles.statusOnline : styles.statusOffline]}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>{health?.data.status === "ok" ? "API" : "Sin API"}</Text>
          </View>
        </View>

        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabBar}>
          {tabs.map((item) => (
            <Pressable key={item.id} onPress={() => setTab(item.id)} style={[styles.tab, tab === item.id && styles.tabActive]} accessibilityRole="tab" accessibilityState={{ selected: tab === item.id }}>
              <Text style={[styles.tabText, tab === item.id && styles.tabTextActive]}>{item.label}</Text>
            </Pressable>
          ))}
        </ScrollView>

        {catalogState === "loading" && <LoadingCard label="Conectando con los catálogos reales..." />}
        {catalogState === "empty" && <StateCard title="Catálogos vacíos" message="La API respondió sin territorios o elecciones." />}
        {catalogState === "error" && <StateCard title="No se pudo conectar" message={catalogError || "La API no está disponible."} actionLabel="Reintentar" onAction={() => setCatalogAttempt((value) => value + 1)} />}

        {catalogState === "ready" && (
          <>
            <SelectionCard territories={territories} territoryId={territoryId} onChange={setTerritoryId} />
            {detailState === "loading" && <LoadingCard label={`Actualizando ${territory?.name || "territorio"}...`} />}
            {detailState === "empty" && <StateCard title="Sin observaciones" message="La API no devolvió historia para este territorio." />}
            {detailState === "error" && <StateCard title="No se pudieron cargar los datos" message={detailError || "Error de datos."} actionLabel="Reintentar" onAction={() => setDetailAttempt((value) => value + 1)} />}
            {detailState !== "loading" && detailState !== "error" && renderTab(tab, {
              territory,
              sourceVersion,
              selectedObservation,
              history,
              prediction,
              predictionError,
              map,
              mapError,
              scenario,
              scenarioState,
              scenarioError,
              calculateScenario,
              question,
              setQuestion,
              assistant,
              assistantState,
              assistantError,
              askAssistant,
            })}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

interface TabProps {
  territory?: Territory;
  sourceVersion: string;
  selectedObservation?: Observation;
  history: Envelope<Observation[]> | null;
  prediction: Envelope<Prediction> | null;
  predictionError: string | null;
  map: Envelope<FeatureCollection> | null;
  mapError: string | null;
  scenario: Envelope<Scenario> | null;
  scenarioState: LoadState;
  scenarioError: string | null;
  calculateScenario: (deltaPp: number) => Promise<void>;
  question: string;
  setQuestion: (value: string) => void;
  assistant: Envelope<AssistantResponse> | null;
  assistantState: LoadState;
  assistantError: string | null;
  askAssistant: () => Promise<void>;
}

function renderTab(tab: TabId, props: TabProps) {
  switch (tab) {
    case "datos":
      return <DataTab {...props} />;
    case "mapa":
      return <MapTab {...props} />;
    case "prediccion":
      return <PredictionTab {...props} />;
    case "escenarios":
      return <ScenarioTab {...props} />;
    case "ayuda":
      return <HelpTab {...props} />;
    default:
      return <HomeTab {...props} />;
  }
}

function HomeTab({ territory, sourceVersion, selectedObservation, history, prediction }: TabProps) {
  return (
    <>
      <View style={styles.hero}>
        <Text style={styles.heroKicker}>LECTURA AGREGADA</Text>
        <Text style={styles.heroTitle}>Comprende la participación ciudadana.</Text>
        <Text style={styles.heroBody}>Datos públicos, estimaciones retrospectivas y límites visibles. Sin perfiles individuales.</Text>
      </View>
      <View style={styles.metricGrid}>
        <Metric label="Observada" value={formatPct(selectedObservation?.participation_pct)} />
        <Metric label="Predicha 2024" value={formatPct(prediction?.data.participation_pct)} />
        <Metric label="Elecciones" value={String(history?.data.length || 0)} />
      </View>
      <Panel title={territory?.name || "Territorio"} eyebrow="Código INE">
        <Text style={styles.body}>Fuente de datos: {sourceVersion}</Text>
        <Text style={styles.muted}>La aplicación consume los artefactos versionados de la API G2.</Text>
      </Panel>
    </>
  );
}

function DataTab({ history }: TabProps) {
  if (!history?.data.length) return <StateCard title="Sin datos históricos" message="No hay observaciones para este territorio." />;
  return (
    <Panel title="Serie histórica" eyebrow="Observado">
      {history.data.map((item) => (
        <View key={item.election_id} style={styles.dataRow}>
          <View>
            <Text style={styles.rowTitle}>{item.year}</Text>
            <Text style={styles.muted}>{item.denominator} · {item.source_id}</Text>
          </View>
          <Text style={styles.rowValue}>{formatPct(item.participation_pct)}</Text>
        </View>
      ))}
    </Panel>
  );
}

function MapTab({ map, mapError }: TabProps) {
  if (mapError && !map) {
    return <StateCard title="Sin geometría verificada" message={`${mapError} CIVIA no dibuja cartografía inventada.`} />;
  }
  if (!map) return <LoadingCard label="Solicitando geometría verificada..." />;
  return (
    <Panel title="Mapa disponible" eyebrow="Cartografía verificable">
      <Text style={styles.body}>{map.data.features.length} geometría(s) GeoJSON recibida(s).</Text>
      <Text style={styles.muted}>La fuente se conserva en la respuesta de la API. La vista móvil no crea polígonos locales.</Text>
    </Panel>
  );
}

function PredictionTab({ prediction, predictionError }: TabProps) {
  if (predictionError && !prediction) return <StateCard title="Predicción no disponible" message={predictionError} />;
  if (!prediction) return <StateCard title="Sin predicción" message="La API todavía no devolvió el artefacto del modelo." />;
  return (
    <>
      <Panel title="Estimación con límites claros" eyebrow="Predicho · backtest retrospectivo">
        <Text style={styles.bigNumber}>{formatPct(prediction.data.participation_pct)}</Text>
        <Text style={styles.body}>Abstención estimada: {formatPct(prediction.data.abstention_pct)}</Text>
        <Text style={styles.muted}>No representa un pronóstico futuro ni una decisión individual.</Text>
      </Panel>
      <View style={styles.metricGrid}>
        <Metric label="MAE" value={`${prediction.data.mae_pp.toFixed(2)} pp`} />
        <Metric label="Baseline" value={`${prediction.data.baseline_mae_pp.toFixed(2)} pp`} />
        <Metric label="Muestra" value={String(prediction.data.n_test)} />
      </View>
      <Panel title="Advertencias" eyebrow="Trazabilidad">
        {prediction.data.warnings.map((warning) => <Text key={warning} style={styles.bullet}>• {warning}</Text>)}
      </Panel>
    </>
  );
}

function ScenarioTab({ scenario, scenarioState, scenarioError, calculateScenario }: TabProps) {
  return (
    <>
      <Panel title="Simulación hipotética" eyebrow="No es una predicción">
        <Text style={styles.body}>Compara cambios en puntos porcentuales sobre la base predicha.</Text>
        <View style={styles.buttonRow}>
          {[-5, 0, 5].map((delta) => <ActionButton key={delta} label={`${delta > 0 ? "+" : ""}${delta} pp`} onPress={() => void calculateScenario(delta)} secondary={delta === 0} />)}
        </View>
        {scenarioState === "loading" && <LoadingCard label="Calculando escenario..." compact />}
        {scenarioState === "error" && <Text style={styles.errorText}>{scenarioError}</Text>}
        {scenario && <Text style={styles.result}>Participación final: {formatPct(scenario.data.final_participation_pct)}</Text>}
      </Panel>
    </>
  );
}

function HelpTab({ question, setQuestion, assistant, assistantState, assistantError, askAssistant }: TabProps) {
  return (
    <>
      <Panel title="Ayuda determinista" eyebrow="Fuente y método">
        <Text style={styles.body}>La tasa usa SV/(SV+NV). NS se informa por separado. La predicción disponible es un backtest retrospectivo 2024.</Text>
        <Text style={styles.muted}>API activa: {API_BASE_URL}</Text>
      </Panel>
      <Panel title="Pregunta sobre el resultado" eyebrow="Asistente">
        <TextInput value={question} onChangeText={setQuestion} style={styles.input} multiline placeholder="Escribe una pregunta" placeholderTextColor="#7d827d" />
        <ActionButton label="Consultar API" onPress={() => void askAssistant()} />
        {assistantState === "loading" && <LoadingCard label="Consultando..." compact />}
        {assistantState === "error" && <Text style={styles.errorText}>{assistantError}</Text>}
        {assistant && <Text style={styles.body}>{assistant.data.answer}</Text>}
      </Panel>
    </>
  );
}

function SelectionCard({ territories, territoryId, onChange }: { territories: Territory[]; territoryId: string; onChange: (value: string) => void }) {
  return (
    <Panel title="Territorio" eyebrow="Selector INE">
      <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.territoryList}>
        {territories.slice(0, 12).map((territory) => <Pressable key={territory.id} onPress={() => onChange(territory.id)} style={[styles.territoryChip, territory.id === territoryId && styles.territoryChipActive]}><Text style={styles.territoryChipText}>{territory.name}</Text></Pressable>)}
      </ScrollView>
      <Text style={styles.muted}>Mostrando los primeros 12 municipios; API total: {territories.length}.</Text>
    </Panel>
  );
}

function Panel({ title, eyebrow, children }: { title: string; eyebrow: string; children: ReactNode }) {
  return <View style={styles.panel}><Text style={styles.eyebrow}>{eyebrow}</Text><Text style={styles.panelTitle}>{title}</Text>{children}</View>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <View style={styles.metric}><Text style={styles.metricLabel}>{label}</Text><Text style={styles.metricValue}>{value}</Text></View>;
}

function LoadingCard({ label, compact = false }: { label: string; compact?: boolean }) {
  return <View style={[styles.stateCard, compact && styles.compactCard]}><ActivityIndicator color="#d9644b" /><Text style={styles.stateTitle}>{label}</Text></View>;
}

function StateCard({ title, message, actionLabel, onAction }: { title: string; message: string; actionLabel?: string; onAction?: () => void }) {
  return <View style={styles.stateCard}><Text style={styles.stateTitle}>{title}</Text><Text style={styles.body}>{message}</Text>{actionLabel && onAction && <ActionButton label={actionLabel} onPress={onAction} />}</View>;
}

function ActionButton({ label, onPress, secondary = false }: { label: string; onPress: () => void; secondary?: boolean }) {
  return <Pressable onPress={onPress} style={({ pressed }) => [styles.actionButton, secondary && styles.actionButtonSecondary, pressed && styles.pressed]} accessibilityRole="button"><Text style={[styles.actionText, secondary && styles.actionTextSecondary]}>{label}</Text></Pressable>;
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: "#f5f0e8" },
  screen: { padding: 20, paddingBottom: 42, gap: 14 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 12 },
  kicker: { color: "#d9644b", fontSize: 11, fontWeight: "800", letterSpacing: 1.5 },
  title: { color: "#18352f", fontSize: 25, fontWeight: "800", marginTop: 5 },
  statusPill: { flexDirection: "row", alignItems: "center", borderRadius: 20, paddingHorizontal: 10, paddingVertical: 7, gap: 5 },
  statusOnline: { backgroundColor: "#dcefe4" },
  statusOffline: { backgroundColor: "#f5d9d1" },
  statusDot: { width: 7, height: 7, borderRadius: 4, backgroundColor: "#d9644b" },
  statusText: { color: "#18352f", fontWeight: "700", fontSize: 12 },
  tabBar: { gap: 8, paddingVertical: 2 },
  tab: { paddingHorizontal: 13, paddingVertical: 9, borderRadius: 20, backgroundColor: "#e8e1d7" },
  tabActive: { backgroundColor: "#18352f" },
  tabText: { color: "#56645d", fontWeight: "700", fontSize: 12 },
  tabTextActive: { color: "#fffaf1" },
  hero: { backgroundColor: "#18352f", borderRadius: 22, padding: 22, gap: 9 },
  heroKicker: { color: "#e7ad79", fontSize: 11, fontWeight: "800", letterSpacing: 1.3 },
  heroTitle: { color: "#fffaf1", fontSize: 27, lineHeight: 33, fontWeight: "800" },
  heroBody: { color: "#c8d6cc", fontSize: 15, lineHeight: 22 },
  metricGrid: { flexDirection: "row", gap: 9 },
  metric: { flex: 1, backgroundColor: "#fffaf1", borderRadius: 16, padding: 13, minHeight: 82, justifyContent: "space-between" },
  metricLabel: { color: "#6f776f", fontSize: 11, fontWeight: "700" },
  metricValue: { color: "#18352f", fontSize: 20, fontWeight: "800" },
  panel: { backgroundColor: "#fffaf1", borderRadius: 18, padding: 17, gap: 9 },
  eyebrow: { color: "#d9644b", fontSize: 10, fontWeight: "800", letterSpacing: 1.2, textTransform: "uppercase" },
  panelTitle: { color: "#18352f", fontSize: 20, fontWeight: "800" },
  body: { color: "#33473f", fontSize: 15, lineHeight: 22 },
  muted: { color: "#778078", fontSize: 12, lineHeight: 18 },
  bigNumber: { color: "#d9644b", fontSize: 46, fontWeight: "900" },
  result: { color: "#18352f", fontSize: 22, fontWeight: "800", marginTop: 6 },
  bullet: { color: "#33473f", fontSize: 13, lineHeight: 20 },
  dataRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 11, borderTopWidth: 1, borderTopColor: "#e8e1d7" },
  rowTitle: { color: "#18352f", fontSize: 17, fontWeight: "800" },
  rowValue: { color: "#d9644b", fontSize: 18, fontWeight: "800" },
  stateCard: { backgroundColor: "#fffaf1", borderRadius: 18, padding: 18, gap: 10, alignItems: "flex-start" },
  compactCard: { padding: 10, flexDirection: "row", alignItems: "center" },
  stateTitle: { color: "#18352f", fontSize: 16, fontWeight: "800" },
  errorText: { color: "#ae422f", fontSize: 14, lineHeight: 20 },
  buttonRow: { flexDirection: "row", gap: 8, flexWrap: "wrap", marginTop: 4 },
  actionButton: { backgroundColor: "#d9644b", borderRadius: 12, paddingHorizontal: 15, paddingVertical: 11, alignSelf: "flex-start" },
  actionButtonSecondary: { backgroundColor: "#e8e1d7" },
  actionText: { color: "#fffaf1", fontWeight: "800", fontSize: 13 },
  actionTextSecondary: { color: "#18352f" },
  pressed: { opacity: 0.72 },
  territoryList: { gap: 8 },
  territoryChip: { backgroundColor: "#e8e1d7", borderRadius: 12, paddingHorizontal: 12, paddingVertical: 10, maxWidth: 170 },
  territoryChipActive: { backgroundColor: "#cfe3d7" },
  territoryChipText: { color: "#18352f", fontSize: 12, fontWeight: "700" },
  input: { minHeight: 70, borderWidth: 1, borderColor: "#d9d1c6", borderRadius: 12, padding: 12, color: "#18352f", textAlignVertical: "top", fontSize: 15 },
});

export default App;
