/**
 * 数据导出工具函数
 */

/**
 * 导出JSON数据为Excel
 * @param data 数据数组
 * @param filename 文件名
 * @param columns 列配置
 */
export function exportToExcel(data: any[], filename: string, columns?: { key: string; label: string }[]) {
  // 如果没有提供列配置，使用第一条数据的键
  const headers = columns 
    ? columns.map(col => col.label)
    : Object.keys(data[0] || {})

  const keys = columns
    ? columns.map(col => col.key)
    : Object.keys(data[0] || {})

  // 创建CSV内容
  let csvContent = '\uFEFF' // UTF-8 BOM
  csvContent += headers.join(',') + '\n'

  data.forEach(row => {
    const values = keys.map(key => {
      const value = row[key]
      // 处理包含逗号、换行等特殊字符的值
      if (value === null || value === undefined) return ''
      const stringValue = String(value)
      if (stringValue.includes(',') || stringValue.includes('\n') || stringValue.includes('"')) {
        return `"${stringValue.replace(/"/g, '""')}"`
      }
      return stringValue
    })
    csvContent += values.join(',') + '\n'
  })

  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  link.setAttribute('href', url)
  link.setAttribute('download', `${filename}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

/**
 * 导出表格数据为CSV
 */
export function exportTableToCSV(tableData: any[], filename: string, columnConfig: any[]) {
  const columns = columnConfig.map(col => ({
    key: col.prop || col.key,
    label: col.label
  })).filter(col => col.key && col.label)

  exportToExcel(tableData, filename, columns)
}
