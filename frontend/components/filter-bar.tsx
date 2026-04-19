import { ChannelItem, PeriodFilter } from "../lib/types";

const PERIOD_OPTIONS: Array<{ value: PeriodFilter; label: string }> = [
  { value: "7d", label: "7d" },
  { value: "30d", label: "30d" },
  { value: "90d", label: "90d" },
  { value: "all", label: "All time" },
];

interface FilterBarProps {
  channels: ChannelItem[];
  selectedChannel: string;
  selectedPeriod: PeriodFilter;
  onChannelChange: (value: string) => void;
  onPeriodChange: (value: PeriodFilter) => void;
  disabled?: boolean;
}


//фильтры периода
export function FilterBar({
  channels,
  selectedChannel,
  selectedPeriod,
  onChannelChange,
  onPeriodChange,
  disabled = false,
}: FilterBarProps) {
  return (
    <section className="filter-card">
      <div className="filter-group">
        <label className="filter-label" htmlFor="channel">
          Channel
        </label>
        <select
          id="channel"
          className="filter-select"
          value={selectedChannel}
          disabled={disabled}
          onChange={(event) => onChannelChange(event.target.value)}
        >
          <option value="">All channels</option>
          {channels.map((channel) => (
            <option key={channel.id} value={channel.username}>
              {channel.title || `@${channel.username}`}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <span className="filter-label">Period</span>
        <div className="period-row">
          {PERIOD_OPTIONS.map((option) => (
            <button
              key={option.value}
              type="button"
              className={option.value === selectedPeriod ? "period-chip active" : "period-chip"}
              disabled={disabled}
              onClick={() => onPeriodChange(option.value)}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
