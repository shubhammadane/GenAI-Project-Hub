import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Navbar } from '../components/layout/Navbar';
import { ThinkingIndicator } from '../components/chat/ThinkingIndicator';
import { ResultTable } from '../components/results/ResultTable';
import type { ExecutionResult, ThinkingStep } from '../types';

describe('AskData Frontend Smoke Tests', () => {
  it('renders Navbar correctly with brand title', () => {
    render(
      <Navbar
        darkMode={false}
        setDarkMode={() => {}}
        tableName="sales_data"
        onNewSession={() => {}}
        onOpenUpload={() => {}}
      />
    );
    expect(screen.getByText('AskData')).toBeDefined();
    expect(screen.getByText('AI Analyst')).toBeDefined();
    expect(screen.getByText('sales_data')).toBeDefined();
  });

  it('renders ThinkingIndicator with active steps', () => {
    const steps: ThinkingStep[] = [
      {
        step: 'understanding',
        title: 'Analyzing schema and question',
        status: 'completed',
        timestamp: 1000,
      },
      {
        step: 'generating_sql',
        title: 'Generating DuckDB SQL',
        status: 'in_progress',
        timestamp: 2000,
      },
    ];

    render(<ThinkingIndicator steps={steps} isStreaming={true} />);
    expect(screen.getByText('Thinking...')).toBeDefined();
    expect(screen.getByText('(1/2 steps)')).toBeDefined();
  });

  it('renders ResultTable with columns and paginated rows', () => {
    const execution: ExecutionResult = {
      columns: ['region', 'sales', 'profit'],
      rows: [
        { region: 'East', sales: 12000, profit: 3200 },
        { region: 'West', sales: 9800, profit: 2100 },
      ],
      row_count: 2,
      execution_time_ms: 12.5,
      truncated: false,
    };

    render(<ResultTable execution={execution} />);
    expect(screen.getByText('East')).toBeDefined();
    expect(screen.getByText('West')).toBeDefined();
    expect(screen.getByText('12.5 ms')).toBeDefined();
    expect(screen.getByText('Export CSV')).toBeDefined();
  });
});
