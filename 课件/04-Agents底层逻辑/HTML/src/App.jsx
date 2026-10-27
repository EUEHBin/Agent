import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './layout/Layout.jsx'
import NeuronPage from './pages/NeuronPage/NeuronPage.jsx'
import ForwardPropagationPage from './pages/ForwardPropagationPage/ForwardPropagationPage.jsx'
import BackPropagationPage from './pages/BackPropagationPage/BackPropagationPage.jsx'
import TokenEmbeddingPage from './pages/TokenEmbeddingPage/TokenEmbeddingPage.jsx'
import AttentionPage from './pages/AttentionPage/AttentionPage.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/neuron" replace />} />
        <Route path="/neuron" element={<NeuronPage />} />
        <Route path="/forward" element={<ForwardPropagationPage />} />
        <Route path="/backward" element={<BackPropagationPage />} />
        <Route path="/embedding" element={<TokenEmbeddingPage />} />
        <Route path="/attention" element={<AttentionPage />} />
      </Route>
    </Routes>
  )
}
