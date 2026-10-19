import { useEffect, useState } from 'react'
import './App.css'

type AlgorithmSummary = {
  slug: string
  title: string
  category: string
  short_description: string
  difficulty: string
}

type AlgorithmDetail = AlgorithmSummary & {
  description: string
  input_data: string
  output_data: string
  preconditions: string
  postconditions: string
  invariant_description: string | null
  pseudocode: string
  default_proof: string
}

type ProofResult = {
  status: string
  duration_ms: number
  diagnostic: string
  engine_available: boolean
}

const apiBase = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api/v1'

function App() {
  const [algorithms, setAlgorithms] = useState<AlgorithmSummary[]>([])
  const [selectedAlgorithm, setSelectedAlgorithm] = useState<AlgorithmDetail | null>(null)
  const [proofCode, setProofCode] = useState('by\n  trivial\n')
  const [catalogError, setCatalogError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isVerifying, setIsVerifying] = useState(false)
  const [result, setResult] = useState<ProofResult | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function loadCatalog() {
      try {
        const response = await fetch(`${apiBase}/algorithms`, { signal: controller.signal })
        if (!response.ok) {
          throw new Error('Не удалось загрузить каталог алгоритмов.')
        }
        const catalog = (await response.json()) as AlgorithmSummary[]
        setAlgorithms(catalog)
      } catch (error) {
        if (!controller.signal.aborted) {
          setCatalogError(
            error instanceof Error ? error.message : 'Не удалось загрузить каталог алгоритмов.',
          )
        }
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    void loadCatalog()
    return () => controller.abort()
  }, [])

  async function openAlgorithm(slug: string) {
    setResult(null)
    try {
      const response = await fetch(`${apiBase}/algorithms/${slug}`)
      if (!response.ok) {
        throw new Error('Не удалось загрузить спецификацию алгоритма.')
      }
      const algorithm = (await response.json()) as AlgorithmDetail
      setSelectedAlgorithm(algorithm)
      setProofCode(algorithm.default_proof)
    } catch (error) {
      setCatalogError(
        error instanceof Error ? error.message : 'Не удалось загрузить спецификацию алгоритма.',
      )
    }
  }

  async function verifyProof() {
    if (!selectedAlgorithm || !proofCode.trim()) {
      return
    }

    setIsVerifying(true)
    setResult(null)
    try {
      const response = await fetch(`${apiBase}/algorithms/${selectedAlgorithm.slug}/verify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ proof_code: proofCode }),
      })
      const body = (await response.json()) as ProofResult | { detail?: string }
      if (!response.ok) {
        throw new Error('detail' in body ? body.detail : 'Не удалось проверить доказательство.')
      }
      setResult(body as ProofResult)
    } catch (error) {
      setResult({
        status: 'request_error',
        duration_ms: 0,
        diagnostic: error instanceof Error ? error.message : 'Не удалось проверить доказательство.',
        engine_available: false,
      })
    } finally {
      setIsVerifying(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="site-header">
        <a className="brand" href="#top" aria-label="Algorithm Correctness Prover">
          <span className="brand-mark">⊢</span>
          <span>ProofLab</span>
        </a>
        <nav aria-label="Основная навигация">
          <a href="#algorithms">Алгоритмы</a>
          <a href="#workspace">Рабочее место</a>
          <a className="nav-login" href="#login">Войти</a>
        </nav>
      </header>

      <section className="hero" id="top">
        <p className="eyebrow">Interactive theorem proving</p>
        <h1>Доказывайте корректность алгоритмов, а не только тестируйте их</h1>
        <p className="hero-copy">
          Веб-среда для изучения формальных спецификаций, инвариантов циклов и
          интерактивных доказательств в Lean 4.
        </p>
        <a className="primary-button" href="#algorithms">
          Открыть каталог <span aria-hidden="true">→</span>
        </a>
      </section>

      <section className="content-section" id="algorithms" aria-labelledby="algorithms-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Библиотека примеров</p>
            <h2 id="algorithms-title">Поддерживаемые алгоритмы</h2>
          </div>
          <span className="catalog-count">{algorithms.length} в каталоге</span>
        </div>

        {isLoading && <p className="notice">Загружаем каталог…</p>}
        {catalogError && <p className="notice notice-error">{catalogError}</p>}
        {!isLoading && !catalogError && (
          <div className="algorithm-grid">
            {algorithms.map((algorithm) => (
              <article className="algorithm-card" key={algorithm.slug}>
                <div className="card-meta">
                  <span>{algorithm.category}</span>
                  <span>{algorithm.difficulty}</span>
                </div>
                <h3>{algorithm.title}</h3>
                <p>{algorithm.short_description}</p>
                <button type="button" onClick={() => void openAlgorithm(algorithm.slug)}>
                  Изучить спецификацию <span aria-hidden="true">→</span>
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="workspace-section" id="workspace" aria-labelledby="workspace-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Рабочее место</p>
            <h2 id="workspace-title">{selectedAlgorithm?.title ?? 'Выберите алгоритм'}</h2>
          </div>
          {selectedAlgorithm && <span className="status-chip">Шаблон доказательства</span>}
        </div>

        {!selectedAlgorithm ? (
          <div className="empty-workspace">
            <p>Выберите алгоритм из каталога, чтобы увидеть его спецификацию и начать доказательство.</p>
          </div>
        ) : (
          <div className="workspace-grid">
            <aside className="specification-panel">
              <h3>Формальная спецификация</h3>
              <p>{selectedAlgorithm.description}</p>
              <dl>
                <div>
                  <dt>Входные данные</dt>
                  <dd>{selectedAlgorithm.input_data}</dd>
                </div>
                <div>
                  <dt>Постусловие</dt>
                  <dd>{selectedAlgorithm.postconditions}</dd>
                </div>
                {selectedAlgorithm.invariant_description && (
                  <div>
                    <dt>Инвариант</dt>
                    <dd>{selectedAlgorithm.invariant_description}</dd>
                  </div>
                )}
              </dl>
              <h4>Псевдокод</h4>
              <pre>{selectedAlgorithm.pseudocode}</pre>
            </aside>

            <div className="proof-panel">
              <div className="editor-heading">
                <div>
                  <h3>Доказательный блок</h3>
                  <p>Введите тактики Lean 4 и отправьте их на проверку.</p>
                </div>
                <span className="file-label">Proof.lean</span>
              </div>
              <label className="sr-only" htmlFor="proof-code">
                Доказательный блок Lean
              </label>
              <textarea
                id="proof-code"
                value={proofCode}
                onChange={(event) => setProofCode(event.target.value)}
                spellCheck="false"
              />
              <div className="editor-actions">
                <button
                  className="primary-button"
                  type="button"
                  onClick={() => void verifyProof()}
                  disabled={isVerifying || !proofCode.trim()}
                >
                  {isVerifying ? 'Проверяем…' : 'Проверить доказательство'}
                </button>
                <p>Для поиска максимума используется проверяемая Lean-модель; формализации остальных алгоритмов добавляются поэтапно.</p>
              </div>
              {result && (
                <div className={`proof-result proof-result-${result.status}`} role="status">
                  <div>
                    <strong>{result.status === 'proved' ? 'Доказательство подтверждено' : 'Результат проверки'}</strong>
                    <span>{result.duration_ms} мс</span>
                  </div>
                  <pre>{result.diagnostic}</pre>
                </div>
              )}
            </div>
          </div>
        )}
      </section>
    </main>
  )
}

export default App
