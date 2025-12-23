import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Audio to Music Video App', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('displays app title and description', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('Audio to Music Video');
    await expect(
      page.getByText('Transform your audio into stunning AI-generated music videos')
    ).toBeVisible();
  });

  test('shows upload step initially', async ({ page }) => {
    await expect(page.getByText('Drop your audio file here')).toBeVisible();
    await expect(page.getByText('Select Audio File')).toBeVisible();
  });

  test('displays progress steps', async ({ page }) => {
    const steps = ['upload', 'analyze', 'customize', 'generate', 'complete'];

    for (const step of steps) {
      await expect(page.getByText(step, { exact: false })).toBeVisible();
    }
  });

  test('highlights current step', async ({ page }) => {
    const uploadStep = page.locator('text=upload').locator('..');
    const stepIndicator = uploadStep.locator('div').first();

    await expect(stepIndicator).toHaveClass(/bg-primary-500/);
  });

  test('allows file selection via file input', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('test-audio.mp3')).toBeVisible();
  });

  test('shows processing state after file upload', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('Processing...')).toBeVisible();
  });

  test('navigates to analysis step after upload', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('Analyzing audio...')).toBeVisible({ timeout: 10000 });
  });

  test('displays audio analysis results', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('Audio Analysis')).toBeVisible({ timeout: 30000 });
    await expect(page.getByText('BPM')).toBeVisible();
    await expect(page.getByText('Mood')).toBeVisible();
    await expect(page.getByText('Genre')).toBeVisible();
  });

  test('shows style customization options', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('Customize Video Style')).toBeVisible({ timeout: 30000 });
    await expect(page.getByText('Cinematic')).toBeVisible();
    await expect(page.getByText('Abstract')).toBeVisible();
  });

  test('allows theme selection', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await page.waitForSelector('[data-testid="theme-cosmic"]', { timeout: 30000 });
    await page.click('[data-testid="theme-cosmic"]');

    await expect(page.getByText('cosmic')).toBeVisible();
  });

  test('allows visual style selection', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await page.waitForSelector('[data-testid="visual-style-anime"]', { timeout: 30000 });
    await page.click('[data-testid="visual-style-anime"]');

    await expect(page.getByText('anime')).toBeVisible();
  });

  test('adjusts effects intensity with slider', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await page.waitForSelector('[data-testid="intensity-slider"]', { timeout: 30000 });

    const slider = page.locator('[data-testid="intensity-slider"]');
    await slider.fill('90');

    await expect(page.getByText('Effects Intensity: 90%')).toBeVisible();
  });

  test('displays generated prompts preview', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('Generated Prompts Preview')).toBeVisible({ timeout: 30000 });
  });

  test('shows generate button when customization is complete', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await expect(page.getByText('Generate Music Video')).toBeVisible({ timeout: 30000 });
  });

  test('complete workflow from upload to generation', async ({ page }) => {
    const testAudioPath = path.join(__dirname, '..', 'fixtures', 'test-audio.mp3');

    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(testAudioPath);

    await page.waitForSelector('text=Audio Analysis', { timeout: 30000 });

    await page.click('[data-testid="theme-nature"]');
    await page.click('[data-testid="visual-style-watercolor"]');

    await page.click('text=Generate Music Video');

    await expect(page.getByText('Generating Video')).toBeVisible({ timeout: 10000 });
  });
});
