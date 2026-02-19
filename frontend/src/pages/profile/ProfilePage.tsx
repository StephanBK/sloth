/**
 * Profile Page - User settings and account management
 *
 * LEARNING NOTE:
 * This page shows user profile info and allows editing.
 * Includes: personal info, diet settings, logout.
 */

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/stores/authStore';
import { userApi } from '@/services/api';
import type { ProfileUpdate } from '@/types';
import { getLevelLabel } from '@/types';

export default function ProfilePage() {
  const { user, logout } = useAuthStore();
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  // Form state
  const [formData, setFormData] = useState<ProfileUpdate>({
    height_cm: user?.height_cm ?? undefined,
    age: user?.age ?? undefined,
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: (data: ProfileUpdate) => userApi.updateProfile(data),
    onSuccess: (updatedUser) => {
      useAuthStore.setState({ user: updatedUser });
      queryClient.invalidateQueries({ queryKey: ['user'] });
      setIsEditing(false);
    },
  });

  const handleSave = () => {
    updateMutation.mutate(formData);
  };

  const handleLogout = async () => {
    await logout();
  };

  if (!user) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      {/* Header */}
      <div className="profile-header">
        <h1>Profil</h1>
        {!isEditing && (
          <button
            className="btn btn-secondary"
            onClick={() => setIsEditing(true)}
          >
            Bearbeiten
          </button>
        )}
      </div>

      {/* Profile Card */}
      <div className="profile-card">
        <div className="profile-avatar">
          <span>{user.email.charAt(0).toUpperCase()}</span>
        </div>
        <div className="profile-email">{user.email}</div>
        <div className="profile-level-badge">
          {getLevelLabel(user.current_level, user.gender)}
        </div>
      </div>

      {/* Stats Overview */}
      <div className="profile-stats">
        <div className="profile-stat">
          <span className="profile-stat-value">
            {user.starting_weight_kg?.toFixed(1) ?? '—'}
          </span>
          <span className="profile-stat-label">Startgewicht (kg)</span>
        </div>
        <div className="profile-stat">
          <span className="profile-stat-value">
            {user.current_weight_kg?.toFixed(1) ?? '—'}
          </span>
          <span className="profile-stat-label">Aktuell (kg)</span>
        </div>
        {user.goal_weight_kg && (
          <div className="profile-stat">
            <span className="profile-stat-value">
              {user.goal_weight_kg.toFixed(1)}
            </span>
            <span className="profile-stat-label">Ziel (kg)</span>
          </div>
        )}
      </div>

      {/* Progress Summary */}
      {user.total_weight_lost !== null && user.total_weight_lost !== undefined && (
        <div className="profile-progress-card">
          <h3>Dein Fortschritt</h3>
          <div className="profile-progress-stats">
            <div>
              <strong>{user.total_weight_lost.toFixed(1)} kg</strong>
              <span>abgenommen</span>
            </div>
            {user.weight_to_lose !== null && user.weight_to_lose !== undefined && (
              <div>
                <strong>{user.weight_to_lose.toFixed(1)} kg</strong>
                <span>noch bis zum Ziel</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Personal Info Section */}
      <div className="profile-section">
        <h2>Persönliche Daten</h2>

        {isEditing ? (
          <div className="profile-form">
            <div className="form-group">
              <label className="form-label">Geschlecht</label>
              <div className="profile-info-value">
                {user.gender === 'male' ? 'Männlich' : 'Weiblich'}
              </div>
              <span className="form-hint">Kann nicht geändert werden</span>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="height">Größe (cm)</label>
              <input
                id="height"
                type="number"
                className="form-input"
                value={formData.height_cm ?? ''}
                onChange={(e) => setFormData({ ...formData, height_cm: parseInt(e.target.value) || undefined })}
                min="100"
                max="250"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="age">Alter</label>
              <input
                id="age"
                type="number"
                className="form-input"
                value={formData.age ?? ''}
                onChange={(e) => setFormData({ ...formData, age: parseInt(e.target.value) || undefined })}
                min="18"
                max="120"
              />
            </div>

            {updateMutation.error && (
              <div className="auth-error">
                Fehler beim Speichern. Bitte versuche es erneut.
              </div>
            )}

            <div className="profile-form-actions">
              <button
                className="btn btn-secondary"
                onClick={() => setIsEditing(false)}
                disabled={updateMutation.isPending}
              >
                Abbrechen
              </button>
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={updateMutation.isPending}
              >
                {updateMutation.isPending ? 'Speichern...' : 'Speichern'}
              </button>
            </div>
          </div>
        ) : (
          <div className="profile-info-list">
            <div className="profile-info-item">
              <span className="profile-info-label">Geschlecht</span>
              <span className="profile-info-value">
                {user.gender === 'male' ? 'Männlich' : 'Weiblich'}
              </span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Größe</span>
              <span className="profile-info-value">
                {user.height_cm ? `${user.height_cm} cm` : '—'}
              </span>
            </div>
            <div className="profile-info-item">
              <span className="profile-info-label">Alter</span>
              <span className="profile-info-value">
                {user.age ? `${user.age} Jahre` : '—'}
              </span>
            </div>
            {user.bmi && (
              <div className="profile-info-item">
                <span className="profile-info-label">BMI</span>
                <span className="profile-info-value">{user.bmi.toFixed(1)}</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Diet Settings Section */}
      <div className="profile-section">
        <h2>Diät-Einstellungen</h2>
        <div className="profile-info-list">
          <div className="profile-info-item">
            <span className="profile-info-label">Kalorienlevel</span>
            <span className="profile-info-value">{getLevelLabel(user.current_level, user.gender)}</span>
          </div>
          {user.dietary_restrictions && user.dietary_restrictions.length > 0 && (
            <div className="profile-info-item">
              <span className="profile-info-label">Ernährungspräferenzen</span>
              <span className="profile-info-value">
                {user.dietary_restrictions.join(', ')}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Account Section */}
      <div className="profile-section">
        <h2>Account</h2>
        <button
          className="btn btn-danger btn-full"
          onClick={() => setShowLogoutConfirm(true)}
        >
          Abmelden
        </button>
      </div>

      {/* Logout Confirmation Modal */}
      {showLogoutConfirm && (
        <div className="modal-overlay" onClick={() => setShowLogoutConfirm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Abmelden?</h2>
              <button className="modal-close" onClick={() => setShowLogoutConfirm(false)}>×</button>
            </div>
            <div className="modal-body">
              <p>Möchtest du dich wirklich abmelden?</p>
            </div>
            <div className="modal-actions" style={{ padding: 'var(--spacing-lg)' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setShowLogoutConfirm(false)}
              >
                Abbrechen
              </button>
              <button
                className="btn btn-danger"
                onClick={handleLogout}
              >
                Abmelden
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
