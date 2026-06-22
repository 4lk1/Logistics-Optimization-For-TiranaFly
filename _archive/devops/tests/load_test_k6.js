import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 }, // ramp up to 100 users
    { duration: '5m', target: 100 }, // stay at 100 users
    { duration: '2m', target: 0 },   // ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000/api';

export default function () {
  // 1. Get Depots
  let res = http.get(`${BASE_URL}/depots`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);

  // 2. Get Coverage
  res = http.get(`${BASE_URL}/coverage?radius=2000`);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);

  // 3. Trigger Optimization (Simulate complex calculation)
  let payload = JSON.stringify({
    p: 5,
    coverage_radius: 3000
  });
  let params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };
  res = http.post(`${BASE_URL}/optimize/p-median`, payload, params);
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(2);
}
