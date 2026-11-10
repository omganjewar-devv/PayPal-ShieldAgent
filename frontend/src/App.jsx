import React, { useState } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  TrendingUp, 
  FileText, 
  DollarSign, 
  Cpu, 
  CheckCircle2, 
  XCircle, 
  RefreshCw,
  Eye,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export default function App() {
  const [selectedDispute, setSelectedDispute] = useState(null);
  const [loading, setLoading] = useState(false);
  const [disputes, setDisputes] = useState([
    {
      id: "PP-D-83921",
      amount: "$149.99",
      reason: "Item Not Received (INR)",
      buyer: "John Doe",
      status: "DEFENDED",
      winProb: 92,
      recommendation: "DEFEND",
      summary: "USPS tracking #9400111899562537628192 confirms delivery to verified postal code 94107 with signature.",
      ce30: false,
      podVerified: true,
      time: "2 hours ago"
    },
    {
      id: "PP-D-99104",
      amount: "$320.00",
      reason: "Unauthorized Payment (Fraud 10.4)",
      buyer: "Sarah Jenkins",
      status: "DEFENDED",
      winProb: 98,
      recommendation: "DEFEND",
      summary: "Visa CE 3.0 matched 2 prior settled transactions (140d & 210d ago) sharing IP 203.0.113.195. Liability shifts to issuer.",
      ce30: true,
      podVerified: false,
      time: "5 hours ago"
    },
    {
      id: "PP-D-10294",
      amount: "$12.50",
      reason: "Significantly Not As Described",
      buyer: "Mike Ross",
      status: "CONCEDED",
      winProb: 38,
      recommendation: "AUTO_CONCEDE",
      summary: "Micro-chargeback below economic defense threshold without carrier POD. Auto-conceded to save $20 network fee.",
      ce30: false,
      podVerified: false,
      time: "1 day ago"
    }
  ]);

  const triggerSimulation = async (type) => {
    setLoading(true);
    try {
      const response = await fetch(`/api/v1/simulate/${type}`, { method: 'POST' });
      if (response.ok) {
        const data = await response.json();
        const newDossier = data.dossier;
        const newDispute = {
          id: data.dispute.dispute_id,
          amount: `$${data.dispute.dispute_amount.value}`,
          reason: data.dispute.reason,
          buyer: data.dispute.buyer_info?.name || "Customer",
          status: newDossier.triage.recommended_action === "DEFEND" ? "DEFENDED" : "CONCEDED",
          winProb: newDossier.triage.win_probability,
          recommendation: newDossier.triage.recommended_action,
          summary: newDossier.defense_summary,
          ce30: newDossier.compliance.visa_ce30_eligible,
          podVerified: newDossier.forensics.pod_verified,
          time: "Just now",
          rawDossier: newDossier
        };
        setDisputes(prev => [newDispute, ...prev]);
        setSelectedDispute(newDispute);
      } else {
        alert("Simulation triggered! Note: Run FastAPI backend at localhost:8000 for live data.");
      }
    } catch (e) {
      alert("Simulation endpoint triggered. Connect backend for live streaming!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-lg text-white tracking-tight">ShieldAgent</h1>
              <span className="text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20 px-2 py-0.5 rounded-full font-medium">PayPal AI Edition</span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Dispute Defense & Visa CE 3.0 Compliance</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-2 animate-pulse"></span>
            PayPal Sandbox Connected
          </span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Protected Volume</span>
              <DollarSign className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-white">$42,850</span>
              <span className="text-xs font-semibold text-emerald-400 flex items-center">+18%</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">Across 182 active disputes</p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Win Rate</span>
              <TrendingUp className="w-4 h-4 text-blue-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-white">91.4%</span>
              <span className="text-xs text-slate-400">vs 41% baseline</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">Powered by CE 3.0 & carrier POD</p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Friendly Fraud Blocked</span>
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-white">$31,200</span>
              <span className="text-xs text-emerald-400 font-semibold">72.8%</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">Triangulated via POD & IP history</p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm">
            <div className="flex justify-between items-start">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Dispute Fees Saved</span>
              <Cpu className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-white">$2,480</span>
              <span className="text-xs text-slate-400">124 claims</span>
            </div>
            <p className="mt-1 text-xs text-slate-500">Auto-conceded micro-disputes</p>
          </div>
        </div>

        {/* Simulation Sandbox Panel */}
        <div className="bg-gradient-to-r from-blue-950/40 via-indigo-950/40 to-slate-900 border border-blue-900/30 rounded-xl p-5">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="text-sm font-semibold text-white flex items-center">
                <Cpu className="w-4 h-4 mr-2 text-blue-400" />
                Dispute Simulation Testbench
              </h2>
              <p className="text-xs text-slate-400 mt-1">
                Simulate inbound PayPal webhooks and watch the multi-agent defense council evaluate evidence in real-time.
              </p>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <button 
                onClick={() => triggerSimulation('friendly-fraud-inr')}
                disabled={loading}
                className="px-3 py-2 text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition shadow-sm flex items-center"
              >
                1. Test INR Friendly Fraud
              </button>
              <button 
                onClick={() => triggerSimulation('visa-ce30-liability-shift')}
                disabled={loading}
                className="px-3 py-2 text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg transition shadow-sm flex items-center"
              >
                2. Test Visa CE 3.0 Match
              </button>
              <button 
                onClick={() => triggerSimulation('unwinnable-micro-chargeback')}
                disabled={loading}
                className="px-3 py-2 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg transition shadow-sm flex items-center"
              >
                3. Test Auto-Concede
              </button>
            </div>
          </div>
        </div>

        {/* Main Content: Dispute Feed & Dossier Inspector */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Dispute Stream (7 cols) */}
          <div className="lg:col-span-7 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-sm flex flex-col">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <h3 className="font-semibold text-sm text-white flex items-center">
                <FileText className="w-4 h-4 mr-2 text-slate-400" />
                Live Inbound Disputes & Defense Stream
              </h3>
              <span className="text-xs text-slate-500">{disputes.length} disputes</span>
            </div>

            <div className="divide-y divide-slate-800/60 overflow-y-auto max-h-[520px]">
              {disputes.map((d) => (
                <div 
                  key={d.id} 
                  onClick={() => setSelectedDispute(d)}
                  className={`p-4 hover:bg-slate-800/40 cursor-pointer transition flex items-center justify-between ${
                    selectedDispute?.id === d.id ? 'bg-slate-800/60 border-l-2 border-blue-500' : ''
                  }`}
                >
                  <div className="space-y-1 pr-4">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-white">{d.id}</span>
                      <span className="text-xs text-slate-400">• {d.buyer}</span>
                      <span className="text-xs text-slate-500">• {d.time}</span>
                    </div>
                    <div className="text-xs text-slate-300 font-medium">{d.reason}</div>
                    <div className="text-xs text-slate-400 line-clamp-1">{d.summary}</div>
                    <div className="flex items-center space-x-2 pt-1">
                      {d.ce30 && (
                        <span className="text-[10px] bg-purple-500/10 text-purple-400 border border-purple-500/20 px-1.5 py-0.5 rounded font-medium">
                          Visa CE 3.0 Liability Shift
                        </span>
                      )}
                      {d.podVerified && (
                        <span className="text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded font-medium">
                          Carrier POD Verified
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="text-right flex flex-col items-end shrink-0">
                    <span className="text-sm font-bold text-white">{d.amount}</span>
                    <span className={`text-[11px] font-bold mt-1 px-2 py-0.5 rounded-full ${
                      d.recommendation === "DEFEND" 
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                        : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                    }`}>
                      {d.recommendation} ({d.winProb}%)
                    </span>
                    <ChevronRight className="w-4 h-4 text-slate-600 mt-2" />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Dossier Inspector (5 cols) */}
          <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-sm flex flex-col">
            <h3 className="font-semibold text-sm text-white flex items-center mb-4">
              <Eye className="w-4 h-4 mr-2 text-slate-400" />
              Defense Dossier & AI Council Audit
            </h3>

            {selectedDispute ? (
              <div className="space-y-4 text-xs">
                <div className="bg-slate-950 p-3.5 rounded-lg border border-slate-800">
                  <div className="flex justify-between items-center mb-2">
                    <span className="font-mono text-slate-400">{selectedDispute.id}</span>
                    <span className="font-bold text-white text-sm">{selectedDispute.amount}</span>
                  </div>
                  <p className="text-slate-300">{selectedDispute.summary}</p>
                </div>

                <div className="space-y-3">
                  <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-800/80">
                    <div className="font-semibold text-slate-200 mb-1 flex items-center">
                      <Cpu className="w-3.5 h-3.5 mr-1.5 text-blue-400" />
                      1. Triage Agent Assessment
                    </div>
                    <div className="text-slate-400">
                      Win Probability: <span className="text-white font-bold">{selectedDispute.winProb}%</span> • 
                      Action: <span className="text-emerald-400 font-bold ml-1">{selectedDispute.recommendation}</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-800/80">
                    <div className="font-semibold text-slate-200 mb-1 flex items-center">
                      <ShieldCheck className="w-3.5 h-3.5 mr-1.5 text-indigo-400" />
                      2. Forensic Auditor Findings
                    </div>
                    <div className="text-slate-400">
                      Proof of Delivery (POD): <span className="text-slate-200">{selectedDispute.podVerified ? "Confirmed via USPS API" : "N/A"}</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-800/80">
                    <div className="font-semibold text-slate-200 mb-1 flex items-center">
                      <CheckCircle2 className="w-3.5 h-3.5 mr-1.5 text-purple-400" />
                      3. Card Network Compliance
                    </div>
                    <div className="text-slate-400">
                      Visa CE 3.0: <span className="text-slate-200">{selectedDispute.ce30 ? "Qualified (Liability Shifted)" : "Not triggered"}</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-800/80">
                    <div className="font-semibold text-slate-200 mb-1 flex items-center">
                      <ExternalLink className="w-3.5 h-3.5 mr-1.5 text-emerald-400" />
                      4. PayPal Disputes REST API Payload
                    </div>
                    <pre className="mt-1.5 p-2 bg-slate-950 rounded text-[11px] text-blue-300 font-mono overflow-x-auto">
{JSON.stringify({
  action: selectedDispute.recommendation === "DEFEND" ? "POST /provide-evidence" : "POST /accept-claim",
  evidence_type: selectedDispute.podVerified ? "PROOF_OF_DELIVERY" : "OTHER",
  notes: selectedDispute.summary
}, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-500">
                <FileText className="w-10 h-10 mb-2 stroke-1" />
                <p className="text-xs">Select any dispute from the live stream to inspect the complete multi-agent defense dossier and PayPal API payload.</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-6 text-center text-xs text-slate-500">
        ShieldAgent • PayPal AI Hackathon 2026 • Autonomous Dispute Defense & Representment Engine
      </footer>
    </div>
  );
}
