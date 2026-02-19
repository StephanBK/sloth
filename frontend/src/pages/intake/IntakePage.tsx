/**
 * Intake Form Page - Multi-screen onboarding
 *
 * LEARNING NOTE:
 * This is a multi-step form with 3 screens:
 * 1. Basic info (gender, height, age)
 * 2. Weight goals (current, goal)
 * 3. Activity & preferences
 *
 * We manage the current screen with useState and
 * save progress after each screen to the backend.
 *
 * TUTORIAL: https://react.dev/learn/sharing-state-between-components
 */

import { useState } from 'react';
import { useAuthStore } from '@/stores/authStore';
import { userApi } from '@/services/api';
import type { Gender, IntakeScreen1, IntakeScreen2, IntakeScreen3, CalorieAwareness } from '@/types';

// Total number of screens
const TOTAL_SCREENS = 3;

export default function IntakePage() {
  // Current screen (1-based for user-friendliness)
  const [currentScreen, setCurrentScreen] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form data for all screens
  const [screen1Data, setScreen1Data] = useState<IntakeScreen1>({
    gender: 'male',
    height_cm: 170,
    age: 30,
  });

  const [screen2Data, setScreen2Data] = useState<IntakeScreen2>({
    current_weight_kg: 80,
  });

  const [screen3Data, setScreen3Data] = useState<IntakeScreen3>({
    calorie_awareness: 'unknown',
    known_calorie_intake: undefined,
    dietary_restrictions: [],
  });

  // Auth store to update user after completion
  const { fetchUser } = useAuthStore();

  /**
   * Go to next screen
   */
  const handleNext = async () => {
    setError(null);
    setIsLoading(true);

    try {
      if (currentScreen === 1) {
        await userApi.saveIntakeScreen1(screen1Data);
        setCurrentScreen(2);
      } else if (currentScreen === 2) {
        await userApi.saveIntakeScreen2(screen2Data);
        setCurrentScreen(3);
      } else if (currentScreen === 3) {
        // Final screen - complete intake
        await userApi.saveIntakeScreen3(screen3Data);
        // Refresh user data (will now have intake_completed: true)
        await fetchUser();
        // Navigation to dashboard happens automatically via IntakeRoute
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ein Fehler ist aufgetreten');
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Go to previous screen
   */
  const handleBack = () => {
    if (currentScreen > 1) {
      setCurrentScreen(currentScreen - 1);
    }
  };

  /**
   * Render progress dots
   */
  const renderProgressDots = () => (
    <div className="intake-progress">
      {Array.from({ length: TOTAL_SCREENS }, (_, i) => {
        const screenNum = i + 1;
        let className = 'intake-progress-dot';
        if (screenNum < currentScreen) className += ' completed';
        if (screenNum === currentScreen) className += ' active';
        return <div key={i} className={className} />;
      })}
    </div>
  );

  /**
   * Render current screen content
   */
  const renderScreen = () => {
    switch (currentScreen) {
      case 1:
        return <Screen1 data={screen1Data} onChange={setScreen1Data} />;
      case 2:
        return <Screen2 data={screen2Data} onChange={setScreen2Data} />;
      case 3:
        return <Screen3 data={screen3Data} onChange={setScreen3Data} />;
      default:
        return null;
    }
  };

  return (
    <div className="intake-page">
      {/* Header with progress */}
      <div className="intake-header">
        <h1>Erzähl uns von dir</h1>
        {renderProgressDots()}
      </div>

      {/* Screen content */}
      <div className="intake-content">
        {error && <div className="auth-error">{error}</div>}
        {renderScreen()}
      </div>

      {/* Footer with buttons */}
      <div className="intake-footer">
        <div className="intake-buttons">
          {currentScreen > 1 && (
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleBack}
              disabled={isLoading}
            >
              Zurück
            </button>
          )}
          <button
            type="button"
            className="btn btn-primary"
            onClick={handleNext}
            disabled={isLoading}
          >
            {isLoading
              ? 'Speichern...'
              : currentScreen === TOTAL_SCREENS
              ? 'Fertig!'
              : 'Weiter'}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// Screen Components
// =============================================================================

interface Screen1Props {
  data: IntakeScreen1;
  onChange: (data: IntakeScreen1) => void;
}

function Screen1({ data, onChange }: Screen1Props) {
  return (
    <div>
      <h2 className="mb-lg">Grundinformationen</h2>

      {/* Gender */}
      <div className="form-group">
        <label className="form-label">Geschlecht</label>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="radio"
              name="gender"
              value="male"
              checked={data.gender === 'male'}
              onChange={() => onChange({ ...data, gender: 'male' as Gender })}
            />
            Männlich
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
            <input
              type="radio"
              name="gender"
              value="female"
              checked={data.gender === 'female'}
              onChange={() => onChange({ ...data, gender: 'female' as Gender })}
            />
            Weiblich
          </label>
        </div>
      </div>

      {/* Height */}
      <div className="form-group">
        <label className="form-label" htmlFor="height">
          Größe (cm)
        </label>
        <input
          id="height"
          type="number"
          className="form-input"
          min={100}
          max={250}
          value={data.height_cm}
          onChange={(e) => onChange({ ...data, height_cm: parseInt(e.target.value) || 0 })}
        />
      </div>

      {/* Age */}
      <div className="form-group">
        <label className="form-label" htmlFor="age">
          Alter
        </label>
        <input
          id="age"
          type="number"
          className="form-input"
          min={16}
          max={100}
          value={data.age}
          onChange={(e) => onChange({ ...data, age: parseInt(e.target.value) || 0 })}
        />
      </div>
    </div>
  );
}

interface Screen2Props {
  data: IntakeScreen2;
  onChange: (data: IntakeScreen2) => void;
}

function Screen2({ data, onChange }: Screen2Props) {
  return (
    <div>
      <h2 className="mb-lg">Dein Gewicht</h2>

      {/* Current weight */}
      <div className="form-group">
        <label className="form-label" htmlFor="currentWeight">
          Aktuelles Gewicht (kg)
        </label>
        <input
          id="currentWeight"
          type="number"
          step="0.1"
          className="form-input"
          min={30}
          max={300}
          value={data.current_weight_kg}
          onChange={(e) => onChange({ ...data, current_weight_kg: parseFloat(e.target.value) || 0 })}
        />
      </div>
    </div>
  );
}

interface Screen3Props {
  data: IntakeScreen3;
  onChange: (data: IntakeScreen3) => void;
}

function Screen3({ data, onChange }: Screen3Props) {
  const calorieOptions: { value: CalorieAwareness; label: string; icon: string }[] = [
    { value: 'gaining', label: 'Ich nehme zu', icon: '↑' },
    { value: 'maintaining', label: 'Ich halte mein Gewicht', icon: '→' },
    { value: 'losing', label: 'Ich nehme ab', icon: '↓' },
  ];

  const dietaryOptions = [
    'vegetarisch',
    'vegan',
    'glutenfrei',
    'laktosefrei',
    'nussallergie',
  ];

  const toggleDietaryRestriction = (restriction: string) => {
    const current = data.dietary_restrictions || [];
    const updated = current.includes(restriction)
      ? current.filter((r) => r !== restriction)
      : [...current, restriction];
    onChange({ ...data, dietary_restrictions: updated });
  };

  const knowsCalories = data.calorie_awareness !== 'unknown';

  return (
    <div>
      <h2 className="mb-lg">Deine Ernährung</h2>

      {/* Calorie awareness */}
      <div className="form-group">
        <label className="form-label">Weißt du ungefähr, wie viele Kalorien du täglich zu dir nimmst?</label>

        {/* Option: I know my calories */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '0.5rem' }}>
          <label className="form-label" style={{ fontSize: '0.9rem', fontWeight: 400, color: 'var(--color-gray-600)' }}>
            Bei dieser Kalorienaufnahme...
          </label>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {calorieOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => onChange({ ...data, calorie_awareness: option.value })}
                style={{
                  flex: '1 1 0',
                  minWidth: '100px',
                  padding: '1rem 0.75rem',
                  border: '2px solid',
                  borderColor: data.calorie_awareness === option.value ? 'var(--color-brand)' : 'var(--color-gray-200)',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: data.calorie_awareness === option.value ? 'rgba(92, 58, 33, 0.06)' : 'transparent',
                  cursor: 'pointer',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: 'all 0.15s ease',
                }}
              >
                <span style={{
                  fontSize: '1.5rem',
                  fontWeight: 700,
                  color: data.calorie_awareness === option.value ? 'var(--color-brand)' : 'var(--color-gray-400)',
                }}>{option.icon}</span>
                <span style={{
                  fontSize: '0.8rem',
                  fontWeight: data.calorie_awareness === option.value ? 600 : 400,
                  color: data.calorie_awareness === option.value ? 'var(--color-brand)' : 'var(--color-gray-600)',
                  textAlign: 'center',
                }}>{option.label}</span>
              </button>
            ))}
          </div>

          {/* Calorie input — only shown when a calorie option is selected */}
          {knowsCalories && (
            <div className="form-group" style={{ marginTop: '0.5rem' }}>
              <label className="form-label" htmlFor="calorieIntake">
                Ungefähre tägliche Kalorienaufnahme (kcal)
              </label>
              <input
                id="calorieIntake"
                type="number"
                className="form-input"
                placeholder="z.B. 2200"
                min={800}
                max={5000}
                step={50}
                value={data.known_calorie_intake ?? ''}
                onChange={(e) => onChange({ ...data, known_calorie_intake: parseInt(e.target.value) || undefined })}
              />
            </div>
          )}

          {/* Divider */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '1rem',
            margin: '0.5rem 0',
          }}>
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-gray-200)' }} />
            <span style={{ fontSize: '0.8rem', color: 'var(--color-gray-400)' }}>oder</span>
            <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--color-gray-200)' }} />
          </div>

          {/* Option: I don't know */}
          <button
            type="button"
            onClick={() => onChange({ ...data, calorie_awareness: 'unknown', known_calorie_intake: undefined })}
            style={{
              padding: '1rem',
              border: '2px solid',
              borderColor: data.calorie_awareness === 'unknown' ? 'var(--color-brand)' : 'var(--color-gray-200)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: data.calorie_awareness === 'unknown' ? 'rgba(92, 58, 33, 0.06)' : 'transparent',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: data.calorie_awareness === 'unknown' ? 600 : 400,
              color: data.calorie_awareness === 'unknown' ? 'var(--color-brand)' : 'var(--color-gray-600)',
              transition: 'all 0.15s ease',
            }}
          >
            Ich weiß nichts über meine Kalorienaufnahme
          </button>

          {data.calorie_awareness === 'unknown' && (
            <p style={{ fontSize: '0.8rem', color: 'var(--color-gray-500)', marginTop: '0.25rem' }}>
              Kein Problem! Wir berechnen einen guten Startwert basierend auf deinem Gewicht.
              Das System korrigiert sich automatisch wöchentlich.
            </p>
          )}
        </div>
      </div>

      {/* Dietary restrictions */}
      <div className="form-group">
        <label className="form-label">Ernährungseinschränkungen (optional)</label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
          {dietaryOptions.map((option) => {
            const isSelected = (data.dietary_restrictions || []).includes(option);
            return (
              <button
                key={option}
                type="button"
                onClick={() => toggleDietaryRestriction(option)}
                style={{
                  padding: '0.5rem 1rem',
                  border: '1px solid',
                  borderColor: isSelected ? 'var(--color-primary)' : 'var(--color-gray-300)',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: isSelected ? 'var(--color-primary)' : 'transparent',
                  color: isSelected ? 'white' : 'var(--color-gray-700)',
                  cursor: 'pointer',
                  fontSize: '0.875rem',
                }}
              >
                {option}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
