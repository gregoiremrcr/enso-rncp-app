type Props = {
  start: string;
  end: string;
  onStart: (value: string) => void;
  onEnd: (value: string) => void;
  onApply: () => void;
  invalid: boolean;
};
export function PeriodFilter({
  start,
  end,
  onStart,
  onEnd,
  onApply,
  invalid,
}: Props) {
  return (
    <form
      onSubmit={(event) => {
        event.preventDefault();
        if (!invalid) onApply();
      }}
    >
      <fieldset className="period-filter">
        <legend>Filtrer la période</legend>
        <label htmlFor="start-date">Du</label>
        <input
          id="start-date"
          type="date"
          value={start}
          onChange={(event) => onStart(event.target.value)}
        />
        <label htmlFor="end-date">Au</label>
        <input
          id="end-date"
          type="date"
          value={end}
          onChange={(event) => onEnd(event.target.value)}
        />
        <button type="submit" disabled={invalid}>
          Appliquer le filtre
        </button>
        {invalid && (
          <p role="alert">La date de début doit précéder la date de fin.</p>
        )}
      </fieldset>
    </form>
  );
}
