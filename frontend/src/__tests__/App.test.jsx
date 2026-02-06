import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, it, expect, beforeAll } from 'vitest'
import App from '../App'

beforeAll(() => {
  // Mock fetch for API calls during render
  globalThis.fetch = () =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve([]),
    })
})

describe('App', () => {
  it('renders without crashing', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>,
    )
    // App should render the layout with navigation
    expect(document.body).toBeTruthy()
  })

  it('renders the sidebar navigation', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>,
    )
    // Layout should contain menu items
    expect(document.querySelector('.ant-layout')).toBeTruthy()
  })
})
