export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

export function randomDelay(min = 200, max = 600): Promise<void> {
  const ms = Math.floor(Math.random() * (max - min)) + min
  return sleep(ms)
}
