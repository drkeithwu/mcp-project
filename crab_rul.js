// 1. 抓取頁面上所有超連結
const links = Array.from(document.querySelectorAll('a'));

// 2. 過濾出有效法規（排除包含「廢止」或「廢除」的項目，並只保留有實際連結的項目）
const validUrls = links
  .filter(a => {
    const text = a.innerText || a.textContent;
    const href = a.href;
    // 確保連結存在，且標題不包含「廢止」或「廢除」
    return href && href.startsWith('http') && !text.includes('廢止') && !text.includes('廢除');
  })
  .map(a => a.href);

// 3. 去除重複的網址（避免圖示與文字連結重複抓取）
const uniqueUrls = [...new Set(validUrls)];

// 4. 在主控台印出結果供確認，並自動複製到剪貼簿
console.log(`✅ 共成功擷取 ${uniqueUrls.length} 個有效法規網址：`);
console.log(uniqueUrls.join('\n'));
copy(uniqueUrls.join('\n'));
alert(`太棒了！已自動為您複製 ${uniqueUrls.length} 個有效法規的網址到剪貼簿囉！`);