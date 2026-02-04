/**
 * Weight Tracking Page - Apple Health inspired
 *
 * LEARNING NOTE:
 * This page shows:
 * 1. Weight progress graph (Recharts)
 * 2. Stats summary (lost, remaining, progress %)
 * 3. Stall detection alert
 * 4. Quick add weight button
 *
 * TUTORIAL: https://recharts.org/en-US/guide/getting-started
 */

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { weightApi } from '@/services/api';
import type { WeightHistory, WeightEntryCreate } from '@/types';

export default function WeightPage() {
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [days, setDays] = useState(30);

  // Fetch weight history
  const { data: weightData, isLoading, error } = useQuery<WeightHistory>({
    queryKey: ['weight-history', days],
    queryFn: () => weightApi.getHistory(days),
  });

  // Add weight mutation
  const addWeightMutation = useMutation({
    mutationFn: (data: WeightEntryCreate) => weightApi.createEntry(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['weight-history'] });
      setShowAddModal(false);
    },
  });

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="weight-page">
        <div className="card">
          <p style={{ color: 'var(--color-error)' }}>
            Fehler beim Laden der Daten. Bitte versuche es erneut.
          </p>
        </div>
      </div>
    );
  }

  const { history, stats, stall_status, entries } = weightData || {
    history: [],
    stats: {},
    stall_status: { can_detect: false, is_stalled: false, message: '', entries_in_period: 0, min_entries_needed: 4 },
    entries: [],
  };

  return (
    <div className="weight-page">
      {/* Header */}
      <div className="weight-header">
        <h1>Gewichtsverlauf</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowAddModal(true)}
        >
          + Gewicht eintragen
        </button>
      </div>

      {/* Stats Cards */}
      <div className="weight-stats-grid">
        <div className="weight-stat-card">
          <span className="weight-stat-label">Start</span>
          <span className="weight-stat-value">
            {stats.starting_weight_kg?.toFixed(1) || '—'} kg
          </span>
        </div>
        <div className="weight-stat-card highlight">
          <span className="weight-stat-label">Aktuell</span>
          <span className="weight-stat-value">
            {stats.current_weight_kg?.toFixed(1) || '—'} kg
          </span>
        </div>
        <div className="weight-stat-card">
          <span className="weight-stat-label">Ziel</span>
          <span className="weight-stat-value">
            {stats.goal_weight_kg?.toFixed(1) || '—'} kg
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      {stats.progress_percent !== null && stats.progress_percent !== undefined && (
        <div className="weight-progress-section">
          <div className="weight-progress-bar">
            <div
              className="weight-progress-fill"
              style={{ width: `${Math.min(100, Math.max(0, stats.progress_percent))}%` }}
            />
          </div>
          <div className="weight-progress-text">
            <span>{stats.total_lost_kg?.toFixed(1) || 0} kg abgenommen</span>
            <span>{stats.progress_percent?.toFixed(0)}%</span>
          </div>
        </div>
      )}

      {/* Stall Alert */}
      {stall_status.can_detect && stall_status.is_stalled && (
        <div className="weight-alert warning">
          <strong>Gewichtsstillstand erkannt!</strong>
          <p>{stall_status.message}</p>
        </div>
      )}

      {/* Not enough data nudge */}
      {!stall_status.can_detect && (
        <div className="weight-alert info">
          <p>{stall_status.message}</p>
        </div>
      )}

      {/* Graph */}
      <div className="weight-graph-card">
        <div className="weight-graph-header">
          <h2>Verlauf</h2>
          <div className="weight-graph-filters">
            {[7, 30, 90].map((d) => (
              <button
                key={d}
                className={`weight-filter-btn ${days === d ? 'active' : ''}`}
                onClick={() => setDays(d)}
              >
                {d}T
              </button>
            ))}
          </div>
        </div>

        {history.length > 0 ? (
          <div className="weight-graph-container">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={history} margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--color-gray-200)" />
                <XAxis
                  dataKey="date"
                  tickFormatter={(date) => {
                    const d = new Date(date);
                    return `${d.getDate()}.${d.getMonth() + 1}`;
                  }}
                  stroke="var(--color-gray-400)"
                  fontSize={12}
                />
                <YAxis
                  domain={['dataMin - 1', 'dataMax + 1']}
                  stroke="var(--color-gray-400)"
                  fontSize={12}
                  tickFormatter={(val) => `${val}`}
                />
                <Tooltip
                  content={<CustomTooltip />}
                />
                {/* Goal line */}
                {stats.goal_weight_kg && (
                  <ReferenceLine
                    y={stats.goal_weight_kg}
                    stroke="var(--color-success)"
                    strokeDasharray="5 5"
                    label={{ value: 'Ziel', position: 'right', fill: 'var(--color-success)', fontSize: 12 }}
                  />
                )}
                {/* Actual measurements - solid line */}
                <Line
                  type="monotone"
                  dataKey="weight_kg"
                  stroke="var(--color-primary)"
                  strokeWidth={2}
                  dot={(props) => <CustomDot {...props} />}
                  activeDot={{ r: 6, fill: 'var(--color-primary)' }}
                  connectNulls={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="weight-graph-empty">
            <p>Noch keine Einträge vorhanden.</p>
            <p className="text-muted">Trage dein erstes Gewicht ein!</p>
          </div>
        )}
      </div>

      {/* Recent Entries */}
      {entries.length > 0 && (
        <div className="weight-entries-card">
          <h2>Letzte Einträge</h2>
          <div className="weight-entries-list">
            {entries.slice(-5).reverse().map((entry) => (
              <div key={entry.id} className="weight-entry-item">
                <span className="weight-entry-date">
                  {new Date(entry.measured_at).toLocaleDateString('de-DE', {
                    weekday: 'short',
                    day: 'numeric',
                    month: 'short',
                  })}
                </span>
                <span className="weight-entry-value">{entry.weight_kg.toFixed(1)} kg</span>
                {entry.notes && <span className="weight-entry-notes">{entry.notes}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Weight Modal */}
      {showAddModal && (
        <AddWeightModal
          onClose={() => setShowAddModal(false)}
          onSubmit={(data) => addWeightMutation.mutate(data)}
          isLoading={addWeightMutation.isPending}
          error={addWeightMutation.error?.message}
        />
      )}
    </div>
  );
}

// =============================================================================
// Custom Components
// =============================================================================

interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: { is_interpolated: boolean };
}

function CustomDot({ cx, cy, payload }: CustomDotProps) {
  if (!cx || !cy) return null;

  // Don't show dots for interpolated points
  if (payload?.is_interpolated) {
    return null;
  }

  return (
    <circle
      cx={cx}
      cy={cy}
      r={4}
      fill="var(--color-primary)"
      stroke="white"
      strokeWidth={2}
    />
  );
}

interface TooltipProps {
  active?: boolean;
  payload?: Array<{ payload: { date: string; weight_kg: number; is_interpolated: boolean } }>;
}

function CustomTooltip({ active, payload }: TooltipProps) {
  if (!active || !payload || !payload.length) return null;

  const data = payload[0].payload;
  const date = new Date(data.date).toLocaleDateString('de-DE', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });

  return (
    <div className="weight-tooltip">
      <p className="weight-tooltip-date">{date}</p>
      <p className="weight-tooltip-value">
        {data.weight_kg.toFixed(1)} kg
        {data.is_interpolated && <span className="text-muted"> (geschätzt)</span>}
      </p>
    </div>
  );
}

// =============================================================================
// Add Weight Modal
// =============================================================================

interface AddWeightModalProps {
  onClose: () => void;
  onSubmit: (data: WeightEntryCreate) => void;
  isLoading: boolean;
  error?: string;
}

function AddWeightModal({ onClose, onSubmit, isLoading, error }: AddWeightModalProps) {
  const [weight, setWeight] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!weight) return;

    onSubmit({
      weight_kg: parseFloat(weight),
      measured_at: date,
      notes: notes || undefined,
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Gewicht eintragen</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          {error && <div className="auth-error">{error}</div>}

          <div className="form-group">
            <label className="form-label" htmlFor="weight">
              Gewicht (kg)
            </label>
            <input
              id="weight"
              type="number"
              step="0.1"
              min="30"
              max="300"
              className="form-input"
              placeholder="z.B. 82.5"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="date">
              Datum
            </label>
            <input
              id="date"
              type="date"
              className="form-input"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              max={new Date().toISOString().split('T')[0]}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="notes">
              Notiz (optional)
            </label>
            <input
              id="notes"
              type="text"
              className="form-input"
              placeholder="z.B. nach dem Sport"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              maxLength={200}
            />
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isLoading}
            >
              Abbrechen
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading || !weight}
            >
              {isLoading ? 'Speichern...' : 'Speichern'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
