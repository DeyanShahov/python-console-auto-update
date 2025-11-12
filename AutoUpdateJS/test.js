// Simple test to verify the modules load correctly
import { VersionInfo, UpdateResult, UpdateCheckResult } from './index.js';

console.log('Testing AutoUpdate JS modules...');

// Test VersionInfo
const version = new VersionInfo({ version: '1.0.0', commit_sha: 'abc123' });
console.log('✅ VersionInfo created:', version.version);

// Test UpdateResult
const successResult = UpdateResult.success(version);
console.log('✅ UpdateResult created:', successResult.isSuccess);

// Test UpdateCheckResult
const checkResult = UpdateCheckResult.noUpdate(version);
console.log('✅ UpdateCheckResult created:', !checkResult.hasUpdate);

console.log('🎉 All basic tests passed!');
