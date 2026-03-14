<template>
  <div class="salary-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h2>薪资管理</h2>
        <div class="header-actions">
          <el-button 
            type="success" 
            @click="showBatchCalculateDialog = true"
            v-if="canCreate"
          >
            <el-icon><DataAnalysis /></el-icon>
            批量计算工资
          </el-button>
          <el-button 
            type="primary" 
            :icon="Plus" 
            @click="showCreateDialog = true"
            v-if="canCreate"
          >
            创建薪资记录
          </el-button>
          <el-button 
            v-else 
            disabled 
            type="info" 
            :icon="Plus"
          >
            创建薪资记录（权限不足）
          </el-button>
        </div>
      </div>
    </div>

    <!-- 搜索筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="年份">
          <el-select v-model="searchForm.year" style="width: 120px">
            <el-option 
              v-for="year in yearOptions" 
              :key="year" 
              :label="year" 
              :value="year" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select v-model="searchForm.month" clearable placeholder="全部" style="width: 120px">
            <el-option 
              v-for="month in monthOptions" 
              :key="month" 
              :label="`${month}月`" 
              :value="month" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="员工">
          <el-select 
            v-model="searchForm.employeeId" 
            clearable 
            filterable
            placeholder="选择员工" 
            style="width: 200px"
          >
            <el-option 
              v-for="emp in departmentEmployees" 
              :key="emp.id" 
              :label="`${emp.name} (${emp.employee_id})`" 
              :value="emp.employee_id" 
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="loadSalaryRecords">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 薪资统计 -->
    <el-card class="stats-card" v-if="statistics">
      <template #header>
        <span>统计信息</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">{{ statistics.total_records }}</div>
            <div class="stat-label">员工数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatAmount(statistics.total_gross_salary) }}</div>
            <div class="stat-label">应发总额</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatAmount(statistics.total_net_salary) }}</div>
            <div class="stat-label">实发总额</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="stat-item">
            <div class="stat-value">¥{{ formatAmount(statistics.avg_gross_salary) }}</div>
            <div class="stat-label">平均薪资</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 薪资记录表格 -->
    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>薪资记录</span>
          <div class="header-actions">
            <el-button :icon="Download" @click="exportSalaryData">导出数据</el-button>
            <el-button :icon="Refresh" @click="loadSalaryRecords">刷新</el-button>
          </div>
        </div>
      </template>
      
      <el-table 
        :data="salaryRecords" 
        v-loading="loading"
        stripe
        border
        :height="400"
      >
        <el-table-column prop="employee_id" label="员工编号" width="120" />
        <el-table-column prop="user_name" label="员工姓名" width="120" />
        <el-table-column prop="year" label="年份" width="80" />
        <el-table-column prop="month" label="月份" width="80">
          <template #default="{ row }">
            {{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column prop="basic_salary" label="基本工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.basic_salary) }}
          </template>
        </el-table-column>
        <el-table-column prop="performance_bonus" label="绩效奖金" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.performance_bonus) }}
          </template>
        </el-table-column>
        <el-table-column prop="gross_salary" label="应发工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.gross_salary) }}
          </template>
        </el-table-column>
        <el-table-column prop="net_salary" label="实发工资" align="right" width="120">
          <template #default="{ row }">
            ¥{{ formatAmount(row.net_salary) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getSalaryStatusType(row.status)">
              {{ getSalaryStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="pay_date" label="发放日期" width="120">
          <template #default="{ row }">
            {{ row.pay_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="320" fixed="right">
          <template #default="{ row }">
            <!-- 查看详情（所有人可见）-->
            <el-button type="primary" size="small" @click="viewSalaryDetail(row)">
              详情
            </el-button>

            <!-- 编辑（仅财务部、管理员、状态为draft）-->
            <el-button 
              type="warning" 
              size="small" 
              @click="editSalary(row)"
              v-if="canEdit(row)"
            >
              编辑
            </el-button>

            <!-- 审核（仅部门经理、本部门）-->
            <el-button 
              type="success" 
              size="small" 
              @click="reviewSalary(row)"
              v-if="canReview(row) && row.status === 'draft'"
            >
              审核
            </el-button>

            <!-- 批准（仅财务部、管理员、状态为manager_reviewed）-->
            <el-button 
              type="danger" 
              size="small" 
              @click="approveSalary(row)"
              v-if="canApprove(row)"
            >
              批准
            </el-button>

            <!-- 发放（仅财务部、管理员、状态为finance_approved）-->
            <el-button 
              type="info" 
              size="small" 
              @click="paySalary(row)"
              v-if="canPay(row)"
            >
              发放
            </el-button>

            <!-- 导出 -->
            <el-dropdown @command="handleCommand" trigger="click">
              <el-button type="info" size="small">
                更多<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item :command="`export-${row.id}`">
                    导出工资单
                  </el-dropdown-item>
                  <el-dropdown-item 
                    :command="`delete-${row.id}`"
                    v-if="canEdit(row)"
                  >
                    删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 创建/编辑薪资记录对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingId ? '编辑薪资记录' : '创建薪资记录'"
      width="800px"
      @close="resetCreateForm"
    >
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="120px">
        <!-- 提示信息 -->
        <el-alert 
          title="财务设置说明" 
          type="info" 
          :closable="false"
          style="margin-bottom: 20px"
        >
          请填写以下基本项目，绩效奖金、加班费、全勤奖将由系统根据员工绩效评估和考勤记录自动计算。
        </el-alert>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="员工" prop="userId">
              <el-select 
                v-model="createForm.userId" 
                filterable
                placeholder="选择员工"
                style="width: 100%"
                :disabled="!!editingId"
                @change="onEmployeeChange"
              >
                <el-option 
                  v-for="emp in departmentEmployees" 
                  :key="emp.id" 
                  :label="`${emp.name} (${emp.employee_id})`" 
                  :value="emp.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="年份" prop="year">
              <el-select v-model="createForm.year" style="width: 100%">
                <el-option 
                  v-for="year in yearOptions" 
                  :key="year" 
                  :label="year" 
                  :value="year" 
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="月份" prop="month">
              <el-select v-model="createForm.month" style="width: 100%">
                <el-option 
                  v-for="month in monthOptions" 
                  :key="month" 
                  :label="`${month}月`" 
                  :value="month" 
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 财务设置项：基本工资和津贴 -->
        <el-divider content-position="left">财务设置项目</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基本工资" prop="basicSalary">
              <el-input-number 
                v-model="createForm.basicSalary" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="津贴补助" prop="allowances">
              <el-input-number 
                v-model="createForm.allowances" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <!-- 扣除项 -->
        <el-divider content-position="left">扣除项目</el-divider>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="社保扣除" prop="socialSecurity">
              <el-input-number 
                v-model="createForm.socialSecurity" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="公积金扣除" prop="housingFund">
              <el-input-number 
                v-model="createForm.housingFund" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="个人所得税" prop="incomeTax">
              <el-input-number 
                v-model="createForm.incomeTax" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="其他扣除" prop="otherDeductions">
              <el-input-number 
                v-model="createForm.otherDeductions" 
                :min="0" 
                :precision="2"
                style="width: 100%" 
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 系统自动计算说明 -->
        <el-divider content-position="left">系统自动计算项目</el-divider>
        
        <el-alert 
          type="warning" 
          :closable="false"
          style="margin-bottom: 15px"
        >
          <template #title>
            以下项目将在保存后由系统根据员工数据自动计算：
          </template>
          <ul style="margin: 5px 0 0 20px; padding: 0;">
            <li><strong>绩效奖金</strong>：根据绩效评估得分和系数自动计算（基本工资 × 奖金基数比例 × 绩效系数）</li>
            <li><strong>加班费</strong>：根据已批准的加班申请记录自动计算（加班小时数 × 时薪）</li>
            <li><strong>全勤奖</strong>：根据考勤记录判断是否符合全勤条件</li>
            <li><strong>考勤扣款</strong>：根据迟到、缺勤、请假记录自动计算扣款</li>
          </ul>
        </el-alert>

        <!-- 计算预览（仅显示财务设置的部分） -->
        <el-card class="calculation-preview">
          <template #header>
            <span>薪资预览（基于财务设置项）</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <div class="calc-item">
                <span class="calc-label">基本收入：</span>
                <span class="calc-value gross">¥{{ formatAmount(calculatedGrossSalary) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="calc-item">
                <span class="calc-label">扣除合计：</span>
                <span class="calc-value deduction">¥{{ formatAmount(calculatedDeductions) }}</span>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="calc-item">
                <span class="calc-label">预计实发：</span>
                <span class="calc-value net">¥{{ formatAmount(calculatedNetSalary) }}</span>
              </div>
            </el-col>
          </el-row>
          <div style="font-size: 12px; color: #909399; margin-top: 10px;">
            * 最终金额将在保存后加入绩效奖金、加班费、全勤奖等系统自动计算项目
          </div>
        </el-card>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createSalaryRecord" :loading="saving">
          {{ editingId ? '保存并计算' : '创建并计算' }}
        </el-button>
      </template>
    </el-dialog>

    <!-- 薪资详情对话框 -->
    <el-dialog v-model="showDetailDialog" title="薪资详情" width="80%">
      <div v-if="selectedSalary" class="salary-detail">
        <!-- 基本信息 -->
        <el-descriptions title="基本信息" border :column="2">
          <el-descriptions-item label="员工信息">
            {{ selectedSalary.user_name }} ({{ selectedSalary.employee_id }})
          </el-descriptions-item>
          <el-descriptions-item label="所属部门">
            {{ selectedSalary.department_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="年月">
            {{ selectedSalary.year }}年{{ selectedSalary.month }}月
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getSalaryStatusType(selectedSalary.status)">
              {{ getSalaryStatusLabel(selectedSalary.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 绩效信息 -->
        <el-descriptions title="绩效信息" border :column="3" style="margin-top: 20px;">
          <el-descriptions-item label="绩效得分">
            {{ selectedSalary.performance_score ? selectedSalary.performance_score.toFixed(1) : '未评定' }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效等级">
            <el-tag v-if="selectedSalary.performance_level" 
                   :type="getPerformanceLevelType(selectedSalary.performance_level)">
              {{ getPerformanceLevelLabel(selectedSalary.performance_level) }}
            </el-tag>
            <span v-else>未评定</span>
          </el-descriptions-item>
          <el-descriptions-item label="绩效系数">
            {{ selectedSalary.performance_coefficient || 1.0 }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效奖金">
            ¥{{ formatAmount(selectedSalary.performance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="考核周期">
            {{ selectedSalary.performance_period_name || '-' }}
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 考勤信息 -->
        <el-descriptions title="考勤信息" border :column="4" style="margin-top: 20px;">
          <el-descriptions-item label="全勤状态">
            <el-tag :type="selectedSalary.is_full_attendance ? 'success' : 'info'">
              {{ selectedSalary.is_full_attendance ? '全勤' : '非全勤' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="全勤奖">
            ¥{{ formatAmount(selectedSalary.full_attendance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="迟到次数">
            {{ selectedSalary.late_count || 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="早退次数">
            {{ selectedSalary.early_leave_count || 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="缺勤次数">
            {{ selectedSalary.absence_count || 0 }} 次
          </el-descriptions-item>
          <el-descriptions-item label="请假天数">
            {{ selectedSalary.leave_days || 0 }} 天
          </el-descriptions-item>
          <el-descriptions-item label="病假天数">
            {{ selectedSalary.sick_leave_days || 0 }} 天
          </el-descriptions-item>
          <el-descriptions-item label="事假天数">
            {{ selectedSalary.personal_leave_days || 0 }} 天
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 薪资明细 -->
        <el-descriptions title="薪资明细" border :column="2" style="margin-top: 20px;">
          <el-descriptions-item label="基本工资">
            ¥{{ formatAmount(selectedSalary.basic_salary) }}
          </el-descriptions-item>
          <el-descriptions-item label="绩效奖金">
            ¥{{ formatAmount(selectedSalary.performance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="津贴补助">
            ¥{{ formatAmount(selectedSalary.allowances) }}
          </el-descriptions-item>
          <el-descriptions-item label="加班费">
            ¥{{ formatAmount(selectedSalary.overtime_pay) }}
          </el-descriptions-item>
          <el-descriptions-item label="全勤奖">
            ¥{{ formatAmount(selectedSalary.full_attendance_bonus) }}
          </el-descriptions-item>
          <el-descriptions-item label="应发工资">
            <span style="color: #67C23A; font-weight: bold;">
              ¥{{ formatAmount(selectedSalary.gross_salary) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 扣款明细 -->
        <el-descriptions title="扣款明细" border :column="2" style="margin-top: 20px;">
          <el-descriptions-item label="社保扣除">
            ¥{{ formatAmount(selectedSalary.social_security) }}
          </el-descriptions-item>
          <el-descriptions-item label="公积金扣除">
            ¥{{ formatAmount(selectedSalary.housing_fund) }}
          </el-descriptions-item>
          <el-descriptions-item label="个人所得税">
            ¥{{ formatAmount(selectedSalary.income_tax) }}
          </el-descriptions-item>
          <el-descriptions-item label="其他扣除">
            ¥{{ formatAmount(selectedSalary.other_deductions) }}
          </el-descriptions-item>
          <el-descriptions-item label="请假扣款">
            <span style="color: #F56C6C;">
              ¥{{ formatAmount(selectedSalary.leave_deduction) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="迟到扣款">
            <span style="color: #F56C6C;">
              ¥{{ formatAmount(selectedSalary.late_deduction) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="缺勤扣款">
            <span style="color: #F56C6C;">
              ¥{{ formatAmount(selectedSalary.absence_deduction) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 最终结算 -->
        <el-descriptions title="最终结算" border :column="2" style="margin-top: 20px;">
          <el-descriptions-item label="实发工资">
            <span style="color: #409EFF; font-weight: bold; font-size: 18px;">
              ¥{{ formatAmount(selectedSalary.net_salary) }}
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="发放日期">
            {{ selectedSalary.pay_date || '未发放' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <el-button 
          v-if="selectedSalary && canEdit(selectedSalary)" 
          type="warning" 
          @click="recalculateSalary(selectedSalary)"
        >
          重新计算
        </el-button>
        <el-button @click="showDetailDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 批量计算对话框 -->
    <el-dialog v-model="showBatchCalculateDialog" title="批量计算工资" width="500px">
      <el-form :model="batchCalculateForm" label-width="100px">
        <el-form-item label="年份" required>
          <el-select v-model="batchCalculateForm.year" style="width: 100%">
            <el-option 
              v-for="year in yearOptions" 
              :key="year" 
              :label="year" 
              :value="year" 
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份" required>
          <el-select v-model="batchCalculateForm.month" style="width: 100%">
            <el-option 
              v-for="month in monthOptions" 
              :key="month" 
              :label="`${month}月`" 
              :value="month" 
            />
          </el-select>
        </el-form-item>
        <el-alert 
          type="info" 
          :closable="false"
          style="margin-top: 10px;"
        >
          <p>批量计算将根据员工的绩效评估和考勤数据自动生成工资记录。</p>
          <p>已在审批流程中的工资记录将被跳过。</p>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="showBatchCalculateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleBatchCalculate" :loading="calculating">
          开始计算
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Download,
  Plus,
  Refresh,
  ArrowDown,
  DataAnalysis
} from '@element-plus/icons-vue'
import api from '@/utils/api'
import { salaryService } from '@/services/salary'
import { useAuthStore } from '@/stores/counter'
import * as permissions from '@/utils/permissions'

// 类型定义
interface DepartmentEmployee {
  id: number
  name: string
  employee_id: string
  base_salary?: number
}

interface SalaryRecord {
  id: number
  user_id: number
  user_name: string
  employee_id: string
  department_name?: string
  year: number
  month: number
  basic_salary: number
  performance_bonus: number
  allowances: number
  overtime_pay: number
  gross_salary: number
  social_security: number
  housing_fund: number
  income_tax: number
  other_deductions: number
  net_salary: number
  status: string
  pay_date?: string
  
  // 绩效关联字段
  performance_evaluation?: number | null
  performance_score?: number | null
  performance_level?: string | null
  performance_level_display?: string | null
  performance_coefficient?: number
  performance_period_name?: string | null
  
  // 全勤奖字段
  full_attendance_bonus?: number
  is_full_attendance?: boolean
  
  // 考勤扣款字段
  leave_deduction?: number
  late_deduction?: number
  absence_deduction?: number
  
  // 考勤统计字段
  leave_days?: number
  sick_leave_days?: number
  personal_leave_days?: number
  other_leave_days?: number
  late_count?: number
  early_leave_count?: number
  absence_count?: number
  actual_work_days?: number
  
  // 用户信息
  user?: {
    id: number
    department?: {
      id: number
      name: string
    }
  }
}

interface SalaryStatistics {
  total_records: number
  total_gross_salary: number
  total_net_salary: number
  avg_gross_salary: number
}

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const calculating = ref(false)
const showCreateDialog = ref(false)
const showDetailDialog = ref(false)
const showBatchCalculateDialog = ref(false)
const createFormRef = ref()
const editingId = ref<number | null>(null)  // 编辑模式记录ID

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const salaryRecords = ref<SalaryRecord[]>([])
const departmentEmployees = ref<DepartmentEmployee[]>([])
const statistics = ref<SalaryStatistics | null>(null)
const selectedSalary = ref<SalaryRecord | null>(null)
const route = useRoute()

// 权限检查（NEW）
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const canCreate = computed(() => permissions.canCreateSalary(user.value as any))
const canEdit = (salary: SalaryRecord) => permissions.canEditSalary(user.value as any, salary.status)
const canReview = (salary: SalaryRecord) => 
  permissions.canReviewSalary(user.value as any, salary.user?.id, salary.user?.department?.id)
const canApprove = (salary: SalaryRecord) => permissions.canApproveSalary(user.value as any, salary.status)
const canPay = (salary: SalaryRecord) => permissions.canPaySalary(user.value as any, salary.status)

// 搜索表单
const searchForm = reactive({
  year: new Date().getFullYear(),
  month: null as number | null,
  employeeId: null as string | null
})

// 创建表单 - 仅包含财务设置的字段
const createForm = reactive({
  userId: null,
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1,
  // 财务设置项
  basicSalary: 0,
  allowances: 0,
  // 扣除项
  socialSecurity: 0,
  housingFund: 0,
  incomeTax: 0,
  otherDeductions: 0
})

// 表单验证规则
const createRules = {
  userId: [{ required: true, message: '请选择员工', trigger: 'change' }],
  year: [{ required: true, message: '请选择年份', trigger: 'change' }],
  month: [{ required: true, message: '请选择月份', trigger: 'change' }],
  basicSalary: [{ required: true, message: '请输入基本工资', trigger: 'blur' }]
}

// 年份选项
const yearOptions = computed(() => {
  const currentYear = new Date().getFullYear()
  return Array.from({ length: 5 }, (_, i) => currentYear - i)
})

// 月份选项
const monthOptions = computed(() => {
  return Array.from({ length: 12 }, (_, i) => i + 1)
})

// 批量计算表单
const batchCalculateForm = reactive({
  year: new Date().getFullYear(),
  month: new Date().getMonth() + 1
})

// 计算预览 - 仅显示财务设置的部分
const calculatedGrossSalary = computed(() => {
  return (createForm.basicSalary || 0) + 
         (createForm.allowances || 0)
})

const calculatedDeductions = computed(() => {
  return (createForm.socialSecurity || 0) + 
         (createForm.housingFund || 0) + 
         (createForm.incomeTax || 0) + 
         (createForm.otherDeductions || 0)
})

const calculatedNetSalary = computed(() => {
  return calculatedGrossSalary.value - calculatedDeductions.value
})

// 方法
const formatAmount = (amount: number | string | null | undefined) => {
  return salaryService.formatAmount(amount)
}

const getSalaryStatusType = (status: string) => {
  return salaryService.getSalaryStatusType(status)
}

const getSalaryStatusLabel = (status: string) => {
  return salaryService.getSalaryStatusLabel(status)
}

// 获取绩效等级类型
const getPerformanceLevelType = (level: string | null | undefined) => {
  return salaryService.getPerformanceLevelType(level)
}

// 获取绩效等级标签
const getPerformanceLevelLabel = (level: string | null | undefined) => {
  return salaryService.getPerformanceLevelLabel(level)
}

// 加载部门员工
const loadDepartmentEmployees = async () => {
  try {
    const response = await api.get('/salary/records/department-employees/')
    departmentEmployees.value = response.data.employees
  } catch (error: any) {
    console.error('获取部门员工失败:', error)
  }
}

// 加载薪资记录
const loadSalaryRecords = async () => {
  loading.value = true
  try {
    const params = {
      year: searchForm.year,
      month: searchForm.month || undefined,
      employee_id: searchForm.employeeId || undefined,
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    const response = await api.get('/salary/records/department-records/', { params })
    salaryRecords.value = response.data.results
    total.value = response.data.count
    
    // 加载统计信息
    await loadStatistics()
  } catch (error: any) {
    console.error('获取薪资记录失败:', error)
    ElMessage.error('获取薪资记录失败')
  } finally {
    loading.value = false
  }
}

// 加载统计信息
const loadStatistics = async () => {
  try {
    const params = {
      year: searchForm.year,
      month: searchForm.month || undefined,
      employee_id: searchForm.employeeId || undefined
    }
    
    const response = await api.get('/salary/statistics/', { params })
    statistics.value = response.data.statistics
  } catch (error: any) {
    console.error('获取统计信息失败:', error)
  }
}

// 重置搜索
const resetSearch = () => {
  searchForm.year = new Date().getFullYear()
  searchForm.month = null
  searchForm.employeeId = null
  currentPage.value = 1
  loadSalaryRecords()
}

// 创建或更新薪资记录
const createSalaryRecord = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    
    saving.value = true
    try {
      // 只发送财务设置的字段，系统自动计算字段由后端处理
      const data = {
        user: createForm.userId,
        year: createForm.year,
        month: createForm.month,
        // 财务设置项
        basic_salary: createForm.basicSalary,
        allowances: createForm.allowances,
        // 扣除项
        social_security: createForm.socialSecurity,
        housing_fund: createForm.housingFund,
        income_tax: createForm.incomeTax,
        other_deductions: createForm.otherDeductions,
        // 启用自动计算
        auto_calculate: true
      }
      
      if (editingId.value) {
        // 更新模式
        await api.patch(`/salary/records/${editingId.value}/`, data)
        ElMessage.success('更新成功，绩效奖金、加班费已自动计算')
      } else {
        // 创建模式
        await api.post('/salary/records/', data)
        ElMessage.success('创建成功，绩效奖金、加班费已自动计算')
      }
      showCreateDialog.value = false
      resetCreateForm()
      await loadSalaryRecords()
    } catch (error: any) {
      console.error('保存薪资记录失败:', error)
      ElMessage.error(error.response?.data?.detail || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

// 重置创建表单
const resetCreateForm = () => {
  editingId.value = null  // 重置编辑模式
  Object.assign(createForm, {
    userId: null,
    year: new Date().getFullYear(),
    month: new Date().getMonth() + 1,
    // 财务设置项
    basicSalary: 0,
    allowances: 0,
    // 扣除项
    socialSecurity: 0,
    housingFund: 0,
    incomeTax: 0,
    otherDeductions: 0
  })
  nextTick(() => {
    createFormRef.value?.clearValidate()
  })
}

// 员工选择变化
const onEmployeeChange = (userId: number) => {
  const employee = departmentEmployees.value.find(emp => emp.id === userId)
  if (employee) {
    createForm.basicSalary = employee.base_salary || 0
  }
}

// 查看薪资详情
const viewSalaryDetail = (salary: any) => {
  selectedSalary.value = salary
  showDetailDialog.value = true
}

// 编辑薪资 - 只填充财务设置的字段
const editSalary = (salary: any) => {
  // 记录编辑模式和ID
  editingId.value = salary.id
  // 填充编辑表单 - 只填充财务可设置的字段
  Object.assign(createForm, {
    userId: salary.user,  // API 返回的是 user (用户ID)
    year: salary.year,
    month: salary.month,
    // 财务设置项
    basicSalary: salary.basic_salary || 0,
    allowances: salary.allowances || 0,
    // 扣除项
    socialSecurity: salary.social_security || 0,
    housingFund: salary.housing_fund || 0,
    incomeTax: salary.income_tax || 0,
    otherDeductions: salary.other_deductions || 0
  })
  showCreateDialog.value = true
}

// 处理下拉菜单命令
const handleCommand = async (command: string) => {
  const [action, id] = command.split('-')
  const salaryId = parseInt(id)
  
  try {
    switch (action) {
      case 'export':
        await salaryService.exportSingleSalary(salaryId)
        break
        
      case 'delete':
        // 找到对应的薪资记录
        const salaryRecord = salaryRecords.value.find(s => s.id === salaryId)
        if (!salaryRecord) {
          ElMessage.error('记录不存在')
          return
        }
        if (!canEdit(salaryRecord)) {
          ElMessage.error('您没有权限删除此薪资')
          return
        }
        await ElMessageBox.confirm('确定要删除这条薪资记录吗？删除后无法恢复。', '确认删除', {
          type: 'warning'
        })
        await api.delete(`/salary/records/${salaryId}/`)
        ElMessage.success('删除成功')
        await loadSalaryRecords()
        break
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 导出薪资数据
const exportSalaryData = async () => {
  try {
    await salaryService.exportSalary({
      year: searchForm.year,
      month: searchForm.month || undefined,
      employee_id: searchForm.employeeId || undefined
    })
  } catch (error: any) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 分页处理
const handleSizeChange = (val: number) => {
  pageSize.value = val
  currentPage.value = 1
  loadSalaryRecords()
}

const handleCurrentChange = (val: number) => {
  currentPage.value = val
  loadSalaryRecords()
}

// 审核薪资（部门经理）
const reviewSalary = async (row: SalaryRecord) => {
  // 权限检查
  if (!canReview(row) || row.status !== 'draft') {
    ElMessage.error('您没有权限审核此薪资')
    return
  }
  
  ElMessageBox.confirm(
    `确认审核 ${row.user_name} 的薪资吗？`,
    '确认审核',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      saving.value = true
      await salaryService.reviewSalary(row.id, 'approve', '')
      ElMessage.success('审核成功')
      loadSalaryRecords()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.error || '审核失败')
    } finally {
      saving.value = false
    }
  }).catch(() => {
    ElMessage.info('已取消审核')
  })
}

// 批准薪资（财务部）
const approveSalary = async (row: SalaryRecord) => {
  // 权限检查
  if (!canApprove(row)) {
    ElMessage.error('您没有权限批准此薪资')
    return
  }
  
  ElMessageBox.confirm(
    `确认批准 ${row.user_name} 的薪资吗？`,
    '确认批准',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      saving.value = true
      await salaryService.approveSalary(row.id, 'approve', '')
      ElMessage.success('批准成功')
      loadSalaryRecords()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.error || '批准失败')
    } finally {
      saving.value = false
    }
  }).catch(() => {
    ElMessage.info('已取消批准')
  })
}

// 发放薪资（财务部）
const paySalary = async (row: SalaryRecord) => {
  // 权限检查
  if (!canPay(row)) {
    ElMessage.error('您没有权限发放此薪资')
    return
  }
  
  ElMessageBox.confirm(
    `确认发放 ${row.user_name} 的薪资吗？`,
    '确认发放',
    {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(async () => {
    try {
      saving.value = true
      const today = new Date().toISOString().split('T')[0]
      await salaryService.paySalary(row.id, today)
      ElMessage.success('发放成功')
      loadSalaryRecords()
    } catch (error: any) {
      ElMessage.error(error.response?.data?.error || '发放失败')
    } finally {
      saving.value = false
    }
  }).catch(() => {
    ElMessage.info('已取消发放')
  })
}

// 批量计算工资
const handleBatchCalculate = async () => {
  if (!batchCalculateForm.year || !batchCalculateForm.month) {
    ElMessage.error('请选择年份和月份')
    return
  }
  
  calculating.value = true
  try {
    const result = await salaryService.batchCalculateSalary({
      year: batchCalculateForm.year,
      month: batchCalculateForm.month
    })
    
    const { summary, results } = result
    
    // 显示结果消息
    let message = `批量计算完成：成功 ${summary.success} 人`
    if (summary.skipped > 0) {
      message += `，跳过 ${summary.skipped} 人`
    }
    if (summary.failed > 0) {
      message += `，失败 ${summary.failed} 人`
    }
    
    if (summary.failed > 0) {
      ElMessage.warning(message)
      console.error('计算失败的员工:', results.failed)
    } else {
      ElMessage.success(message)
    }
    
    showBatchCalculateDialog.value = false
    await loadSalaryRecords()
  } catch (error: any) {
    console.error('批量计算失败:', error)
    ElMessage.error(error.response?.data?.error || '批量计算失败')
  } finally {
    calculating.value = false
  }
}

// 重新计算单个员工工资
const recalculateSalary = async (salary: any) => {
  if (!salary || !canEdit(salary)) {
    ElMessage.error('无法重新计算此工资记录')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      '确定要重新计算此工资记录吗？将根据最新的绩效和考勤数据重新计算。',
      '确认重新计算',
      { type: 'warning' }
    )
    
    calculating.value = true
    const result = await salaryService.recalculateSalary(salary.id)
    
    ElMessage.success('重新计算完成')
    selectedSalary.value = result.salary_record
    await loadSalaryRecords()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('重新计算失败:', error)
      ElMessage.error(error.response?.data?.error || '重新计算失败')
    }
  } finally {
    calculating.value = false
  }
}

// 初始化
onMounted(() => {
  // 从路由查询中预填筛选条件，便于从员工列表跳转
  const { employee_id, year, month } = route.query
  if (typeof employee_id === 'string') {
    searchForm.employeeId = employee_id
  }
  if (typeof year === 'string' && !Number.isNaN(Number(year))) {
    searchForm.year = Number(year)
  }
  if (typeof month === 'string' && !Number.isNaN(Number(month))) {
    searchForm.month = Number(month)
  }
  
  // 确保用户信息已加载（特别是在刷新页面时）
  if (!authStore.user) {
    authStore.fetchUserInfo()
  }
  
  loadDepartmentEmployees()
  loadSalaryRecords()
})
</script>

<style scoped>
.salary-management {
  padding: var(--hr-space-lg);
}

.page-header {
  margin-bottom: var(--hr-space-lg);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-content h2 {
  margin: 0;
  font-size: 22px;
  color: var(--color-text-primary);
  font-weight: 700;
}

.search-card,
.stats-card,
.table-card {
  margin-bottom: var(--hr-space-lg);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: var(--hr-space-sm);
}

.stat-item {
  text-align: center;
  padding: var(--hr-space-lg);
}

.stat-value {
  font-size: 24px;
  font-weight: 800;
  color: var(--hr-primary);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.pagination-container {
  margin-top: var(--hr-space-lg);
  text-align: right;
}

.calculation-preview {
  margin-top: var(--hr-space-lg);
}

.calc-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: var(--hr-radius-sm);
  transition: background var(--hr-transition-fast);
}

.calc-item:hover {
  background: var(--hr-gray-50);
}

.calc-label {
  font-weight: 500;
  color: var(--color-text-regular);
  font-size: 14px;
}

.calc-value {
  font-weight: 700;
  font-size: 16px;
}

.calc-value.gross {
  color: var(--hr-primary);
}

.calc-value.deduction {
  color: var(--hr-danger);
}

.calc-value.net {
  color: var(--hr-success);
}

.salary-detail {
  padding: var(--hr-space-lg) 0;
}
</style>
