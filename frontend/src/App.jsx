import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"
import SpotDetail from "./pages/SpotDetail/SpotDetail.jsx"
import SpotList from "./pages/SpotList/SpotList.jsx"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<SpotList />} />
        <Route path="/spots/:slug" element={<SpotDetail />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
