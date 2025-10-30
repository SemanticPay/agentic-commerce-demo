export async function queryAgent(question: string, sessionId?: string) {
  const res = await fetch('http://0.0.0.0:8001/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId }),
  })
  if (!res.ok) throw new Error(`Server error: ${res.status}`)
  return (await res.json()) as {
    response: string
    status: string
    session_id?: string
    widgets: any[]
  }
}