import { useEffect, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { api, ApiRequestError } from "./api";
import type {
  AssistantResponse,
  Election,
  Envelope,
  FeatureCollection,
  Health,
  Observation,
  Prediction,
  Scenario,
  Source,
  Territory,
} from "./types";

type ViewId = "inicio" | "datos" | "mapa" | "prediccion" | "escenarios" | "ayuda";
type AsyncStatus = "idle" | "loading" | "ready" | "empty" | "error";

const navItems: Array<{ id: ViewId; label: string; number: string }> = [
  { id: "inicio", label: "Inicio", number: "⌂" },
  { id: "datos", label: "Datos", number: "▥" },
  { id: "mapa", label: "Mapa", number: "◇" },
  { id: "prediccion", label: "Predicción", number: "↗" },
  { id: "escenarios", label: "Escenarios", number: "☷" },
  { id: "ayuda", label: "Ayuda", number: "?" },
];

function viewFromHash(): ViewId {
  const value = window.location.hash.replace("#", "") as ViewId;
  return navItems.some((item) => item.id === value) ? value : "inicio";
}

function formatPct(value: number | null | undefined): string {
  return value === null || value === undefined ? "Sin datos" : `${value.toFixed(1)}%`;
}

function formatDate(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return new Intl.DateTimeFormat("es-MX", { dateStyle: "medium" }).format(date);
}

function errorMessage(error: unknown): string {
  if (error instanceof ApiRequestError) return error.message;
  if (error instanceof Error) return error.message;
  return "No se pudo completar la solicitud.";
}

function App() {
  const [view, setView] = useState<ViewId>(() => viewFromHash());
  const [catalogAttempt, setCatalogAttempt] = useState(0);
  const [catalogStatus, setCatalogStatus] = useState<AsyncStatus>("loading");
  const [detailAttempt, setDetailAttempt] = useState(0);
  const [catalogError, setCatalogError] = useState<string | null>(null);
  const [health, setHealth] = useState<Envelope<Health> | null>(null);
  const [territories, setTerritories] = useState<Territory[]>([]);
  const [elections, setElections] = useState<Election[]>([]);
  const [territoryId, setTerritoryId] = useState("");
  const [electionId, setElectionId] = useState("");
  const [chartLeft, setChartLeft] = useState("");
  const [chartRight, setChartRight] = useState("");
  const [detailStatus, setDetailStatus] = useState<AsyncStatus>("idle");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [history, setHistory] = useState<Envelope<Observation[]> | null>(null);
  const [prediction, setPrediction] = useState<Envelope<Prediction> | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);
  const [map, setMap] = useState<Envelope<FeatureCollection> | null>(null);
  const [mapError, setMapError] = useState<string | null>(null);
  const [scenario, setScenario] = useState<Envelope<Scenario> | null>(null);
  const [scenarioStatus, setScenarioStatus] = useState<AsyncStatus>("idle");
  const [scenarioError, setScenarioError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setCatalogStatus("loading");
    setCatalogError(null);
    Promise.all([api.getHealth(), api.getTerritories(), api.getElections()])
      .then(([healthResponse, territoryResponse, electionResponse]) => {
        if (!active) return;
        const nextTerritories = territoryResponse.data;
        const nextElections = electionResponse.data;
        setHealth(healthResponse);
        setTerritories(nextTerritories);
        setElections(nextElections);
        setTerritoryId((current) => current || nextTerritories[0]?.id || "");
        setElectionId((current) => current || nextElections.at(-1)?.election_id || "");
        setChartLeft(
          (current) => current || nextElections.find((item) => item.year === 2018)?.election_id || nextElections[0]?.election_id || "",
        );
        setChartRight(
          (current) => current || nextElections.find((item) => item.year === 2024)?.election_id || nextElections.at(-1)?.election_id || "",
        );
        setCatalogStatus(nextTerritories.length && nextElections.length ? "ready" : "empty");
      })
      .catch((error: unknown) => {
        if (!active) return;
        setCatalogStatus("error");
        setCatalogError(errorMessage(error));
      });
    return () => {
      active = false;
    };
  }, [catalogAttempt]);

  useEffect(() => {
    window.history.replaceState(null, "", `#${view}`);
  }, [view]);

  useEffect(() => {
    if (!territoryId) return;
    let active = true;
    setDetailStatus("loading");
    setDetailError(null);
    setPredictionError(null);
    setMapError(null);
    setHistory(null);
    setPrediction(null);
    setMap(null);
    setScenario(null);
    setScenarioStatus("idle");

    const mapRequest = view === "mapa" ? api.getMap(territoryId) : Promise.resolve(null);
    Promise.allSettled([api.getParticipation(territoryId), api.getPrediction(territoryId), mapRequest]).then(
      ([historyResult, predictionResult, mapResult]) => {
        if (!active) return;

        if (historyResult.status === "fulfilled") {
          setHistory(historyResult.value);
          setDetailStatus(historyResult.value.data.length ? "ready" : "empty");
        } else {
          setDetailStatus("error");
          setDetailError(errorMessage(historyResult.reason));
        }

        if (predictionResult.status === "fulfilled") {
          setPrediction(predictionResult.value);
        } else {
          setPredictionError(errorMessage(predictionResult.reason));
        }

        if (mapResult.status === "fulfilled" && mapResult.value) {
          setMap(mapResult.value);
        } else if (mapResult.status === "rejected") {
          setMapError(errorMessage(mapResult.reason));
        }
      },
    );

    return () => {
      active = false;
    };
  }, [territoryId, detailAttempt, view]);

  const currentTerritory = territories.find((item) => item.id === territoryId);
  const currentElection = elections.find((item) => item.election_id === electionId);
  const selectedObservation = history?.data.find((item) => item.election_id === electionId);
  const sourceVersion = history?.meta.source_version || health?.meta.source_version || "Pendiente de API";

  async function calculateScenario(deltaPp: number) {
    if (!territoryId) return;
    setScenarioStatus("loading");
    setScenarioError(null);
    try {
      const response = await api.getScenario(territoryId, deltaPp);
      setScenario(response);
      setScenarioStatus("ready");
    } catch (error) {
      setScenario(null);
      setScenarioStatus("error");
      setScenarioError(errorMessage(error));
    }
  }

  const retryCatalog = () => setCatalogAttempt((attempt) => attempt + 1);
  const retryDetail = () => setDetailAttempt((attempt) => attempt + 1);

  return (
    <div className="app-frame">
      <aside className="side-rail" aria-label="Navegación principal">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            C
          </div>
          <div>
            <strong>CIVIA</strong>
            <span>Datos para comprender</span>
          </div>
        </div>
        <nav className="main-nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${view === item.id ? "is-active" : ""}`}
              type="button"
              aria-current={view === item.id ? "page" : undefined}
              onClick={() => setView(item.id)}
            >
              <span className="nav-number">{item.number}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
        <div className="rail-note">
          <span className="eyebrow">Corte de datos</span>
          <strong>{sourceVersion}</strong>
          <p>Participación agregada. Sin perfiles individuales ni recomendaciones partidistas.</p>
        </div>
      </aside>

      <main className="content-column">
        <header className="topbar">
          <div>
            <span className="eyebrow">CIVIA　›　{navItems.find((item) => item.id === view)?.label}</span>
            <p className="topbar-title">Datos para comprender</p>
          </div>
          <div className={`api-status ${health?.data.status === "ok" ? "is-online" : ""}`}>
            <span className="status-dot" aria-hidden="true" />
            {health ? (health.data.status === "ok" ? "API conectada" : "API degradada") : "Conectando API"}
          </div>
        </header>

        {catalogStatus === "ready" && (
          <SelectionBar
            territories={territories}
            elections={elections}
            territoryId={territoryId}
            electionId={electionId}
            onTerritoryChange={setTerritoryId}
            onElectionChange={(value) => {
              setElectionId(value);
              setScenario(null);
              setScenarioStatus("idle");
            }}
          />
        )}

        {catalogStatus === "loading" && <LoadingPanel label="Conectando con los catálogos reales de CIVIA…" />}
        {catalogStatus === "empty" && (
          <StatePanel title="No hay catálogos disponibles" message="La API respondió sin territorios o elecciones para mostrar." />
        )}
        {catalogStatus === "error" && (
          <StatePanel title="No se pudo conectar con CIVIA" message={catalogError || "La API no está disponible."} actionLabel="Reintentar" onAction={retryCatalog} />
        )}

        {catalogStatus === "ready" && (
          <>
            <div className="page-heading">
              <div>
                <span className="eyebrow">{currentElection?.year || "Vista general"} · {currentTerritory?.name || "Territorio"}</span>
                <h1>{({ inicio: "Comprende la participación ciudadana", datos: "Explora los datos históricos", mapa: "La participación en el territorio", prediccion: "Estimación con límites claros", escenarios: "¿Qué cambia bajo tus supuestos?", ayuda: "Entiende cada resultado" } as Record<ViewId, string>)[view]}</h1>
              </div>
              <span className="version-chip">Fuente {sourceVersion}</span>
            </div>
            {detailStatus === "loading" && <LoadingPanel label={`Actualizando ${currentTerritory?.name || "territorio"}…`} compact />}
            {detailStatus === "error" && <StatePanel title="No se pudieron cargar los datos" message={detailError || "La API devolvió un error."} actionLabel="Reintentar" onAction={retryDetail} />}
            {detailStatus !== "error" && (
              <ViewContent
                view={view}
                territory={currentTerritory}
                election={currentElection}
                selectedObservation={selectedObservation}
                history={history?.data || []}
                historyEnvelope={history}
                prediction={prediction?.data || null}
                predictionError={predictionError}
                map={map}
                mapError={mapError}
                scenario={scenario?.data || null}
                scenarioStatus={scenarioStatus}
                scenarioError={scenarioError}
                calculateScenario={calculateScenario}
                elections={elections}
                chartLeft={chartLeft}
                chartRight={chartRight}
                setChartLeft={setChartLeft}
                setChartRight={setChartRight}
                health={health?.data || null}
                onNavigate={setView}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

interface SelectionBarProps {
  territories: Territory[];
  elections: Election[];
  territoryId: string;
  electionId: string;
  onTerritoryChange: (value: string) => void;
  onElectionChange: (value: string) => void;
}

function SelectionBar({ territories, elections, territoryId, electionId, onTerritoryChange, onElectionChange }: SelectionBarProps) {
  return (
    <section className="selection-bar" aria-label="Selección de datos">
      <label>
        <span>Territorio</span>
        <select value={territoryId} onChange={(event) => onTerritoryChange(event.target.value)}>
          {territories.map((territory) => (
            <option key={territory.id} value={territory.id}>
              {territory.name} · {territory.id}
            </option>
          ))}
        </select>
      </label>
      <label>
        <span>Elección de referencia</span>
        <select value={electionId} onChange={(event) => onElectionChange(event.target.value)}>
          {elections.map((election) => (
            <option key={election.election_id} value={election.election_id}>
              {election.year} · {election.election_type === "federal_concurrente" ? "Concurrente" : "Intermedia"}
            </option>
          ))}
        </select>
      </label>
      <div className="selection-code">
        <span className="eyebrow">Código INE</span>
        <strong>{territoryId || "—"}</strong>
      </div>
    </section>
  );
}

interface ViewContentProps {
  view: ViewId;
  territory?: Territory;
  election?: Election;
  selectedObservation?: Observation;
  history: Observation[];
  historyEnvelope: Envelope<Observation[]> | null;
  prediction: Prediction | null;
  predictionError: string | null;
  map: Envelope<FeatureCollection> | null;
  mapError: string | null;
  scenario: Scenario | null;
  scenarioStatus: AsyncStatus;
  scenarioError: string | null;
  calculateScenario: (deltaPp: number) => Promise<void>;
  elections: Election[];
  chartLeft: string;
  chartRight: string;
  setChartLeft: (value: string) => void;
  setChartRight: (value: string) => void;
  health: Health | null;
  onNavigate: (view: ViewId) => void;
}

function ViewContent(props: ViewContentProps) {
  switch (props.view) {
    case "datos":
      return <DataView {...props} />;
    case "mapa":
      return <MapView {...props} />;
    case "prediccion":
      return <PredictionView {...props} />;
    case "escenarios":
      return <ScenarioView {...props} />;
    case "ayuda":
      return <HelpView key={props.territory?.id} {...props} />;
    default:
      return <HomeView {...props} />;
  }
}

function HomeView({ territory, election, selectedObservation, history, historyEnvelope, prediction, scenario, elections, chartLeft, chartRight, setChartLeft, setChartRight, onNavigate }: ViewContentProps) {
  return (
    <>
      <section className="hero-panel">
        <div className="hero-copy">
          <span className="hero-kicker">CIVIA / lectura agregada</span>
          <h2>Comprende la participación ciudadana</h2>
          <p>Explora datos históricos, estimaciones y escenarios con transparencia.</p>
          <div className="hero-actions">
            <button className="button button-light" type="button" onClick={() => onNavigate("datos")}>Abrir históricos <span aria-hidden="true">↗</span></button>
            <span className="hero-footnote">Datos públicos · municipios INE · Jalisco</span>
          </div>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <span className="orbit-line orbit-line-one" />
          <span className="orbit-line orbit-line-two" />
          <span className="orbit-dot orbit-dot-one" />
          <span className="orbit-dot orbit-dot-two" />
          <span className="orbit-label">SV / (SV + NV)</span>
        </div>
      </section>

      <section className="metric-grid" aria-label="Resumen de datos">
        <MetricCard label="Participación observada" value={formatPct(selectedObservation?.participation_pct)} detail={election ? `Elección federal ${election.year} · ${territory?.name}` : "Sin elección"} tone="observed" />
        <MetricCard label="Abstención estimada" value={election?.election_id === "federal-2024" ? formatPct(prediction?.abstention_pct) : "No disponible"} detail={`Elección federal ${election?.year || ""} · ${territory?.name || ""}`} tone="predicted" />
        <MetricCard label="Elecciones disponibles" value={`${history.length}`} detail="En el periodo consultado" tone="neutral" />
      </section>

      <section className="content-grid home-grid">
        <div className="panel panel-large">
          <PanelHeader eyebrow="Evolución histórica de la participación" title="Porcentaje de participación ciudadana" action={<button className="text-button" type="button" onClick={() => onNavigate("datos")}>Ver datos ↗</button>} />
          <HistoryChart observations={history} elections={elections} leftId={chartLeft} rightId={chartRight} onLeftChange={setChartLeft} onRightChange={setChartRight} />
        </div>
        <aside className="panel insight-panel">
          <span className="eyebrow">Vista territorial</span>
          <h3>{territory?.name || "Territorio seleccionado"}</h3>
          <p>La cartografía solo aparece cuando la API entrega geometría verificada; mientras tanto, Mapa conserva una alternativa accesible.</p>
          <div className="insight-rule" />
          <span className="mini-label">Participación observada</span>
          <strong>{formatPct(selectedObservation?.participation_pct)}</strong>
          <span className="mini-label">Estado de cartografía</span>
          <strong>Consultar geometría verificada</strong>
          <button className="button button-light full-button" type="button" onClick={() => onNavigate("mapa")}>Ver estado del mapa</button>
        </aside>
      </section>

      <section className="home-actions" aria-label="Explora CIVIA">
        <button className="home-action-card" type="button" onClick={() => onNavigate("datos")}><strong>Consultar datos</strong><span>Explora los resultados históricos y sus fuentes.</span><small>{history.length} elecciones disponibles · {territory?.name}</small></button>
        <button className="home-action-card" type="button" onClick={() => onNavigate("prediccion")}><strong>Ver predicción</strong><span>Consulta la estimación y las métricas del modelo.</span><small>Predicción agregada · datos de API</small></button>
        <button className="home-action-card" type="button" onClick={() => onNavigate("escenarios")}><strong>Simular escenario</strong><span>Compara cambios hipotéticos en la participación.</span><small>{scenario ? `Último escenario: ${formatPct(scenario.final_participation_pct)}` : "Ejercicio hipotético"}</small></button>
      </section>
      <button className="methodology-link" type="button" onClick={() => onNavigate("ayuda")}><strong>Metodología y transparencia</strong><span>Conoce las fuentes de datos, el enfoque de estimación y sus límites.</span><b>Ver metodología　→</b></button>

      <DataSources sources={historyEnvelope?.sources || []} />
    </>
  );
}

function DataView({ territory, history, historyEnvelope, elections, chartLeft, chartRight, setChartLeft, setChartRight }: ViewContentProps) {
  return (
    <>
      <section className="section-intro">
        <span className="eyebrow">Observado · serie histórica</span>
        <h2>Explora los datos históricos</h2>
        <p>Consulta y compara elecciones con fuentes verificables.</p>
      </section>
      <section className="panel panel-large">
        <PanelHeader eyebrow="Comparador" title="Elige las dos elecciones a contrastar" />
        <HistoryChart observations={history} elections={elections} leftId={chartLeft} rightId={chartRight} onLeftChange={setChartLeft} onRightChange={setChartRight} />
      </section>
      <section className="panel table-panel">
        <PanelHeader eyebrow="Detalle verificable" title="Serie completa" />
        {history.length ? <HistoryTable observations={history} /> : <EmptyBlock title="Sin registros" message="La API no devolvió observaciones para este territorio." />}
      </section>
      <DataSources sources={historyEnvelope?.sources || []} />
    </>
  );
}

function PredictionView({ election, prediction, predictionError, historyEnvelope }: ViewContentProps) {
  if (election?.election_id !== "federal-2024") {
    return <UnavailablePanel title="Predicción limitada al backtest 2024" message="El contrato actual solo sirve una estimación retrospectiva para federal-2024. Selecciona esa elección para ver métricas reales." />;
  }
  if (predictionError && !prediction) {
    return <StatePanel title="Predicción no disponible" message={predictionError} />;
  }
  if (!prediction) {
    return <EmptyBlock title="Sin predicción cargada" message="La API todavía no devolvió un artefacto de modelo para este territorio." />;
  }
  return (
    <>
      <section className="prediction-banner">
        <div>
        <span className="eyebrow">Predicho · backtest retrospectivo</span>
          <h2>Estimación con límites claros</h2>
          <p>Resultados agregados, nunca decisiones individuales. Esta estimación retrospectiva no representa un pronóstico futuro.</p>
        </div>
        <div className="prediction-number">
          <span>Participación</span>
          <strong>{formatPct(prediction.participation_pct)}</strong>
          <small>Abstención estimada: {formatPct(prediction.abstention_pct)}</small>
        </div>
      </section>
      <section className="metric-grid prediction-metrics">
        <MetricCard label="MAE del modelo" value={`${prediction.mae_pp.toFixed(2)} pp`} detail="Error absoluto medio" tone="predicted" />
        <MetricCard label="MAE baseline" value={`${prediction.baseline_mae_pp.toFixed(2)} pp`} detail="Elección comparable" tone="neutral" />
        <MetricCard label="Muestra de prueba" value={`${prediction.n_test}`} detail="Municipios" tone="neutral" />
        <MetricCard label="Intervalo" value={prediction.interval ? `${formatPct(prediction.interval.lower)}—${formatPct(prediction.interval.upper)}` : "No disponible"} detail={prediction.interval ? "Cobertura calibrada" : "Sin bloque de calibración"} tone="warning" />
      </section>
      <section className="content-grid two-thirds-grid">
        <div className="panel warning-panel">
          <span className="eyebrow">Advertencias del modelo</span>
          <h3>Lee el resultado con contexto.</h3>
          <ul className="plain-list">
            {prediction.warnings.map((warning) => <li key={warning}>{warning}</li>)}
          </ul>
        </div>
        <div className="panel metadata-panel">
          <span className="eyebrow">Trazabilidad</span>
          <dl className="metadata-list">
            <div><dt>Modelo</dt><dd>{prediction.model_version}</dd></div>
            <div><dt>Estrategia</dt><dd>{prediction.strategy}</dd></div>
            <div><dt>Evaluación</dt><dd>{prediction.evaluation_mode}</dd></div>
            <div><dt>Fuente</dt><dd>{historyEnvelope?.meta.source_version || "API"}</dd></div>
          </dl>
        </div>
      </section>
    </>
  );
}

function MapView({ territory, history, map, mapError }: ViewContentProps) {
  const latest = history.find((item) => item.year === 2024);
  if (mapError && !map) {
    return (
      <>
        <section className="section-intro">
          <span className="eyebrow">Mapa · cartografía verificable</span>
          <h2>La geometría todavía no está disponible.</h2>
          <p>CIVIA no dibuja un mapa ilustrativo como si fuera un dato. Cuando la API entregue GeoJSON verificado, esta vista lo mostrará junto con su fuente.</p>
        </section>
        <section className="content-grid two-thirds-grid">
          <div className="panel map-empty-panel">
            <div className="map-empty-icon" aria-hidden="true">⌁</div>
            <span className="eyebrow">Estado de cartografía</span>
            <h3>Sin geometría verificada</h3>
            <p>{mapError}</p>
            <span className="status-tag status-warning">No se dibuja un mapa falso</span>
          </div>
          <div className="panel alternative-panel">
            <span className="eyebrow">Alternativa accesible</span>
            <h3>Lista de datos del territorio</h3>
            <dl className="metadata-list">
              <div><dt>Municipio</dt><dd>{territory?.name || "Sin datos"}</dd></div>
              <div><dt>Clave INE</dt><dd>{territory?.id || "Sin datos"}</dd></div>
              <div><dt>Participación 2024</dt><dd>{formatPct(latest?.participation_pct)}</dd></div>
              <div><dt>Abstención 2024</dt><dd>{formatPct(latest?.abstention_pct)}</dd></div>
              <div><dt>Denominador</dt><dd>{latest?.denominator || "Sin datos"}</dd></div>
            </dl>
          </div>
        </section>
      </>
    );
  }
  if (!map) return <EmptyBlock title="Mapa sin respuesta" message="La API todavía no devolvió una colección geográfica." />;
  return (
    <section className="panel map-ready-panel">
      <span className="eyebrow">GeoJSON verificado</span>
      <h2>Cartografía disponible para {territory?.name}</h2>
      <p>{map.data.features.length} elemento(s) geográfico(s) devueltos por la API.</p>
      <GeoJsonMap features={map.data.features} territoryName={territory?.name || "territorio seleccionado"} />
      <div className="geojson-summary" role="region" aria-label="Resumen accesible del GeoJSON">
        <strong>Leyenda</strong>
        <span><i className="legend-swatch" aria-hidden="true" /> Territorio seleccionado</span>
        <span>Fuente: {map.meta.source_version}</span>
      </div>
      <ul className="plain-list">
        {map.data.features.map((feature, index) => <li key={`${String(feature.properties.territory_id)}-${index}`}>Territorio: {String(feature.properties.name || feature.properties.territory_id || "Sin etiqueta")}</li>)}
      </ul>
    </section>
  );
}

type Coordinate = [number, number];
type GeoBounds = { minX: number; maxX: number; minY: number; maxY: number };

function isCoordinate(value: unknown): value is Coordinate {
  return Array.isArray(value) && value.length >= 2 && typeof value[0] === "number" && typeof value[1] === "number";
}

function flattenCoordinates(value: unknown): Coordinate[] {
  if (isCoordinate(value)) return [[value[0], value[1]]];
  if (!Array.isArray(value)) return [];
  return value.flatMap((child) => flattenCoordinates(child));
}

function getGeoBounds(features: FeatureCollection["features"]): GeoBounds | null {
  const coordinates = features.flatMap((feature) => flattenCoordinates(feature.geometry?.coordinates));
  if (!coordinates.length) return null;
  return coordinates.reduce<GeoBounds>(
    (bounds, [x, y]) => ({
      minX: Math.min(bounds.minX, x),
      maxX: Math.max(bounds.maxX, x),
      minY: Math.min(bounds.minY, y),
      maxY: Math.max(bounds.maxY, y),
    }),
    { minX: coordinates[0][0], maxX: coordinates[0][0], minY: coordinates[0][1], maxY: coordinates[0][1] },
  );
}

function makeProjector(bounds: GeoBounds) {
  const width = 720;
  const height = 390;
  const padding = 28;
  const spanX = Math.max(bounds.maxX - bounds.minX, 0.000001);
  const spanY = Math.max(bounds.maxY - bounds.minY, 0.000001);
  const scale = Math.min((width - padding * 2) / spanX, (height - padding * 2) / spanY);
  const offsetX = (width - spanX * scale) / 2;
  const offsetY = (height - spanY * scale) / 2;
  return ([x, y]: Coordinate): [number, number] => [offsetX + (x - bounds.minX) * scale, height - (offsetY + (y - bounds.minY) * scale)];
}

function geometryPaths(value: unknown, project: (coordinate: Coordinate) => [number, number], close: boolean): string[] {
  if (!Array.isArray(value) || !value.length || isCoordinate(value)) return [];
  if (value.every(isCoordinate)) {
    const points = value.map((coordinate) => {
      const [x, y] = project(coordinate);
      return `${x.toFixed(2)},${y.toFixed(2)}`;
    });
    return [`M ${points.join(" L ")}${close ? " Z" : ""}`];
  }
  return value.flatMap((child) => geometryPaths(child, project, close));
}

function GeoJsonMap({ features, territoryName }: { features: FeatureCollection["features"]; territoryName: string }) {
  const bounds = getGeoBounds(features);
  if (!bounds) return <EmptyBlock title="GeoJSON sin coordenadas" message="La API devolvió una colección sin coordenadas dibujables." />;
  const project = makeProjector(bounds);
  return (
    <div className="geo-map-shell">
      <svg viewBox="0 0 720 390" role="img" aria-labelledby="geo-map-title geo-map-description">
        <title id="geo-map-title">Geometría verificada de {territoryName}</title>
        <desc id="geo-map-description">Representación proporcional de las geometrías devueltas por la API de CIVIA.</desc>
        <rect className="geo-map-background" x="0" y="0" width="720" height="390" rx="10" />
        {[1, 2, 3, 4, 5].map((step) => <line key={`vertical-${step}`} className="geo-map-grid-line" x1={step * 120} x2={step * 120} y1="0" y2="390" />)}
        {[1, 2, 3].map((step) => <line key={`horizontal-${step}`} className="geo-map-grid-line" x1="0" x2="720" y1={step * 97.5} y2={step * 97.5} />)}
        {features.map((feature, index) => {
          const geometry = feature.geometry;
          const type = typeof geometry?.type === "string" ? geometry.type : "";
          const coordinates = geometry?.coordinates;
          const paths = geometryPaths(coordinates, project, type === "Polygon" || type === "MultiPolygon");
          const point = type === "Point" && isCoordinate(coordinates) ? project(coordinates) : null;
          return (
            <g key={`${String(feature.properties.territory_id)}-${index}`} className="geo-feature">
              {paths.map((path, pathIndex) => <path key={pathIndex} d={path} />)}
              {point && <circle cx={point[0]} cy={point[1]} r="7" />}
            </g>
          );
        })}
      </svg>
      <p className="geo-map-note">Representación proporcional del GeoJSON verificado; la lista inferior mantiene una alternativa textual.</p>
    </div>
  );
}

function ScenarioView({ election, scenario, scenarioStatus, scenarioError, calculateScenario, prediction }: ViewContentProps) {
  const [deltaInput, setDeltaInput] = useState("0");
  const [validationError, setValidationError] = useState<string | null>(null);

  if (election?.election_id !== "federal-2024") {
    return <UnavailablePanel title="Escenario limitado al backtest 2024" message="El backend calcula escenarios únicamente sobre la base predicha de federal-2024." />;
  }

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const delta = Number(deltaInput);
    if (!Number.isFinite(delta) || delta < -20 || delta > 20) {
      setValidationError("Usa un valor entre -20 y +20 puntos porcentuales.");
      return;
    }
    setValidationError(null);
    void calculateScenario(delta);
  }

  return (
    <>
      <section className="section-intro scenario-intro">
        <span className="eyebrow">Simulado · hipotético</span>
        <h2>¿Qué cambia bajo tus supuestos?</h2>
        <p>Explora cómo un cambio en la participación modifica el resultado, a partir de un escenario hipotético.</p>
      </section>
      <section className="content-grid scenario-grid">
        <div className="panel scenario-form-panel">
          <form onSubmit={submit}>
            <label className="range-label" htmlFor="delta-range">Variación hipotética</label>
            <div className="range-value"><strong>{Number(deltaInput) > 0 ? "+" : ""}{deltaInput || "0"}</strong><span>puntos porcentuales</span></div>
            <input id="delta-range" type="range" min="-20" max="20" step="0.1" value={deltaInput || "0"} onChange={(event) => setDeltaInput(event.target.value)} aria-describedby="delta-help" />
            <div className="range-scale" aria-hidden="true"><span>-20 pp</span><span>0</span><span>+20 pp</span></div>
            <label className="number-label" htmlFor="delta-number">Escribe el valor exacto</label>
            <div className="number-input-wrap"><input id="delta-number" type="number" min="-20" max="20" step="0.1" value={deltaInput} onChange={(event) => setDeltaInput(event.target.value)} /><span>pp</span></div>
            <p id="delta-help" className="field-help">El valor se limita a -20/+20 pp. La aritmética final la devuelve la API.</p>
            {validationError && <p className="field-error" role="alert">{validationError}</p>}
            <button className="button button-primary full-button" type="submit" disabled={scenarioStatus === "loading"}>{scenarioStatus === "loading" ? "Calculando…" : "Calcular escenario"}</button>
          </form>
        </div>
        <div className="panel scenario-result-panel">
          {scenarioStatus === "error" && <StatePanel title="No se pudo calcular" message={scenarioError || "La API rechazó el escenario."} />}
          {scenarioStatus !== "error" && !scenario && <EmptyBlock title="Sin escenario calculado" message="El resultado aparecerá aquí después de consultar la API." />}
          {scenario && (
            <>
              <div className="result-heading"><span className="eyebrow">Respuesta de API</span><span className="status-tag status-simulated">{scenario.label}</span></div>
              <div className="scenario-numbers">
                <div><span>Base predicha</span><strong>{formatPct(scenario.base_participation_pct)}</strong></div>
                <div className="scenario-arrow" aria-hidden="true">→</div>
                <div><span>Resultado final</span><strong>{formatPct(scenario.final_participation_pct)}</strong></div>
              </div>
              <div className="scenario-bars" role="img" aria-label={`Participación base ${formatPct(scenario.base_participation_pct)} y escenario ${formatPct(scenario.final_participation_pct)}`}>
                <div><span style={{ height: `${Math.max(0, Math.min(100, scenario.base_participation_pct))}%` }} /><small>Base</small></div>
                <div><span style={{ height: `${Math.max(0, Math.min(100, scenario.final_participation_pct))}%` }} /><small>Escenario</small></div>
              </div>
              <div className="scenario-detail-grid">
                <div><span>Abstención final</span><strong>{formatPct(scenario.final_abstention_pct)}</strong></div>
                <div><span>Delta devuelto</span><strong>{scenario.delta_pp > 0 ? "+" : ""}{scenario.delta_pp} pp</strong></div>
              </div>
              <p className="scenario-disclaimer">{scenario.clamped ? "La API saturó el resultado en el límite permitido." : "Cálculo aritmético hipotético; no demuestra causalidad."}</p>
            </>
          )}
          {!scenario && prediction && <p className="result-footnote">Base disponible en predicción: {formatPct(prediction.participation_pct)}.</p>}
        </div>
      </section>
    </>
  );
}

function HelpView({ health, territory, historyEnvelope }: ViewContentProps) {
  const [question, setQuestion] = useState("");
  const [assistant, setAssistant] = useState<AssistantResponse | null>(null);
  const [assistantStatus, setAssistantStatus] = useState<AsyncStatus>("idle");
  const [assistantError, setAssistantError] = useState<string | null>(null);

  async function submitQuestion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!territory || !question.trim() || !health?.ai_enabled) return;
    setAssistantStatus("loading");
    setAssistantError(null);
    try {
      const response = await api.askAssistant(territory.id, question.trim());
      setAssistant(response.data);
      setAssistantStatus("ready");
    } catch (error) {
      setAssistantStatus("error");
      setAssistantError(errorMessage(error));
    }
  }

  return (
    <>
      <section className="section-intro help-intro">
        <span className="eyebrow">Ayuda · lectura determinista</span>
        <h2>Entiende cada resultado</h2>
        <p>Fuentes, metodología y respuestas claras.</p>
      </section>
      <section className="help-grid">
        <article className="help-card help-card-dark"><span className="help-index">01</span><h3>¿Qué significa observado?</h3><p>Es un resultado histórico de los registros agregados para una elección concreta. No es una estimación.</p></article>
        <article className="help-card"><span className="help-index">02</span><h3>¿Qué significa predicho?</h3><p>Es una salida del modelo evaluado retrospectivamente. Aquí solo se sirve el backtest 2024 y su error.</p></article>
        <article className="help-card"><span className="help-index">03</span><h3>¿Qué significa simulado?</h3><p>Es una operación hipotética devuelta por el backend. No prueba que una intervención produzca ese efecto.</p></article>
        <article className="help-card"><span className="help-index">04</span><h3>¿Qué se cuenta?</h3><p>La participación usa SV/(SV+NV). NS se muestra por separado y no se convierte en abstención.</p></article>
      </section>
      <section className="content-grid two-thirds-grid">
        <div className="panel source-panel">
          <PanelHeader eyebrow="Transparencia" title="Cada cifra lleva contexto" />
          <p>Consulta el territorio, la elección, la fuente y la versión de datos junto con cada resultado.</p>
          <DataSources sources={historyEnvelope?.sources || []} />
        </div>
        <div className="panel assistant-panel">
          <span className="eyebrow">Asistente opcional</span>
          <h3>{health?.ai_enabled ? "Pregunta sobre este territorio" : "Asistente generativo desactivado"}</h3>
          {!health?.ai_enabled && <p>La experiencia central funciona con ayuda determinista y no requiere una clave de IA.</p>}
          {health?.ai_enabled && (
            <form onSubmit={submitQuestion}>
              <label htmlFor="assistant-question">Pregunta</label>
              <textarea id="assistant-question" maxLength={1000} value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Escribe una pregunta sobre los datos…" />
              <button className="button button-primary" type="submit" disabled={assistantStatus === "loading"}>{assistantStatus === "loading" ? "Consultando…" : "Consultar"}</button>
              {assistantError && <p className="field-error" role="alert">{assistantError}</p>}
              {assistant && <div className="assistant-answer"><span className="status-tag">{assistant.mode}</span><p>{assistant.answer}</p></div>}
            </form>
          )}
        </div>
      </section>
    </>
  );
}

function HistoryChart({ observations, elections, leftId, rightId, onLeftChange, onRightChange }: { observations: Observation[]; elections: Election[]; leftId: string; rightId: string; onLeftChange: (value: string) => void; onRightChange: (value: string) => void }) {
  const selected = [observations.find((item) => item.election_id === leftId), observations.find((item) => item.election_id === rightId)].filter(Boolean) as Observation[];
  if (!observations.length) return <EmptyBlock title="Sin histórico" message="No hay registros para graficar." />;
  const chartWidth = 640;
  const chartHeight = 230;
  const baseline = 190;
  const plotHeight = 150;
  const groupWidth = chartWidth / Math.max(selected.length, 1);
  return (
    <div className="chart-block">
      <div className="chart-controls">
        <label><span>Elección A</span><select value={leftId} onChange={(event) => onLeftChange(event.target.value)}>{elections.map((item) => <option key={item.election_id} value={item.election_id}>{item.year}</option>)}</select></label>
        <label><span>Elección B</span><select value={rightId} onChange={(event) => onRightChange(event.target.value)}>{elections.map((item) => <option key={item.election_id} value={item.election_id}>{item.year}</option>)}</select></label>
      </div>
      <div className="chart-legend" aria-label="Leyenda de la gráfica"><span><i className="legend-swatch observed-swatch" aria-hidden="true" />Participación</span><span><i className="legend-swatch abstention-swatch" aria-hidden="true" />Abstención</span></div>
      <svg className="history-chart" viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label="Comparación proporcional de participación y abstención en dos elecciones">
        {[0, 25, 50, 75, 100].map((tick) => { const y = baseline - (tick / 100) * plotHeight; return <g key={tick}><line x1="42" x2="620" y1={y} y2={y} className="chart-grid-line" /><text x="32" y={y + 4} textAnchor="end" className="chart-axis-label">{tick}</text></g>; })}
        {selected.map((item, index) => { const center = 42 + groupWidth * index + groupWidth / 2; const pHeight = (item.participation_pct / 100) * plotHeight; const aHeight = (item.abstention_pct / 100) * plotHeight; return <g key={`${item.election_id}-${index}`}><rect x={center - 44} y={baseline - pHeight} width="32" height={pHeight} rx="8" className="chart-bar chart-bar-observed"><title>{item.year}: participación {formatPct(item.participation_pct)}</title></rect><rect x={center - 6} y={baseline - aHeight} width="32" height={aHeight} rx="8" className="chart-bar chart-bar-abstention"><title>{item.year}: abstención {formatPct(item.abstention_pct)}</title></rect><text x={center - 6} y="216" textAnchor="middle" className="chart-year-label">{item.year}</text></g>; })}
      </svg>
      <p className="chart-note">Porcentajes entre registros con condición conocida. La tabla inferior conserva conteos y faltantes.</p>
    </div>
  );
}

function HistoryTable({ observations }: { observations: Observation[] }) {
  return (
    <div className="table-scroll">
      <table>
        <caption>Histórico de participación observada</caption>
        <thead><tr><th scope="col">Elección</th><th scope="col">Participación</th><th scope="col">Abstención</th><th scope="col">NS</th><th scope="col">Conocidos</th><th scope="col">Fuente</th></tr></thead>
        <tbody>{observations.map((item) => <tr key={item.election_id}><th scope="row">{item.year}</th><td><strong>{formatPct(item.participation_pct)}</strong></td><td>{formatPct(item.abstention_pct)}</td><td>{item.unknown_count.toLocaleString("es-MX")} ({formatPct(item.unknown_pct)})</td><td>{item.known_count.toLocaleString("es-MX")}</td><td><span className="source-code">{item.source_id}</span></td></tr>)}</tbody>
      </table>
    </div>
  );
}

function DataSources({ sources }: { sources: Source[] }) {
  return (
    <section className="source-strip" aria-label="Fuentes consultadas">
      <div><span className="eyebrow">Fuentes</span><strong>{sources.length ? `${sources.length} registro(s) trazable(s)` : "Sin fuentes devueltas"}</strong></div>
      {sources.length > 0 && <ul>{sources.map((source) => <li key={source.id}><a href={source.url} target="_blank" rel="noreferrer">{source.title}</a><span>{formatDate(source.retrieved_at)}</span></li>)}</ul>}
    </section>
  );
}

function PanelHeader({ eyebrow, title, action }: { eyebrow: string; title: string; action?: ReactNode }) {
  return <div className="panel-header"><div><span className="eyebrow">{eyebrow}</span><h3>{title}</h3></div>{action}</div>;
}

function MetricCard({ label, value, detail, tone }: { label: string; value: string; detail: string; tone: "observed" | "predicted" | "simulated" | "warning" | "neutral" }) {
  return <article className={`metric-card metric-${tone}`}><div className="metric-top"><span>{label}</span><span className="metric-mark" aria-hidden="true" /></div><strong>{value}</strong><small>{detail}</small></article>;
}

function LoadingPanel({ label, compact = false }: { label: string; compact?: boolean }) {
  return <div className={`loading-panel ${compact ? "loading-compact" : ""}`} role="status"><span className="loading-spinner" aria-hidden="true" />{label}</div>;
}

function StatePanel({ title, message, actionLabel, onAction }: { title: string; message: string; actionLabel?: string; onAction?: () => void }) {
  return <div className="state-panel" role="alert"><span className="state-icon" aria-hidden="true">!</span><div><h2>{title}</h2><p>{message}</p>{actionLabel && onAction && <button className="button button-primary" type="button" onClick={onAction}>{actionLabel}</button>}</div></div>;
}

function UnavailablePanel({ title, message }: { title: string; message: string }) {
  return <section className="panel unavailable-panel"><span className="eyebrow">No disponible para esta selección</span><h2>{title}</h2><p>{message}</p></section>;
}

function EmptyBlock({ title, message }: { title: string; message: string }) {
  return <div className="empty-block"><span className="empty-symbol" aria-hidden="true">∅</span><strong>{title}</strong><p>{message}</p></div>;
}

export default App;
