<template>
  <div class="performance-management">
    <el-card class="page-header">
      <div class="header-content">
        <h2>绩效管理</h2>
        <p>管理绩效周期、模板和全公司绩效数据</p>
      </div>
    </el-card>

    <!-- 统计概览 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#409EFF"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalPeriods }}</div>
              <div class="stat-label">绩效周期</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#67C23A"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalTemplates }}</div>
              <div class="stat-label">绩效模板</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">            <div class="stat-icon">
              <el-icon size="32" color="#E6A23C"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalGoals }}</div>
              <div class="stat-label">绩效目标</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon size="32" color="#F56C6C"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalEvaluations }}</div>
              <div class="stat-label">绩效评估</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 标签页 -->
    <el-card class="main-content">
      <el-tabs v-model="activeTab" @tab-click="handleTabClick">
        <!-- 绩效周期管理 -->
        <el-tab-pane label="绩效周期" name="periods">
          <div class="tab-content">
            <div class="tab-header">
              <h3>绩效周期管理</h3>
              <el-button type="primary" @click="showAddPeriodDialog">
                <el-icon><Plus /></el-icon>
                新建周期
              </el-button>
            </div>
            
            <el-table :data="periods" v-loading="periodsLoading" stripe>
              <el-table-column prop="name" label="周期名称" />
              <el-table-column prop="period_type" label="周期类型">
                <template #default="{ row }">
                  <el-tag :type="getPeriodTypeTagType(row.period_type)">
                    {{ getPeriodTypeLabel(row.period_type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="start_date" label="开始日期" />
              <el-table-column prop="end_date" label="结束日期" />
              <el-table-column prop="is_active" label="状态">
                <template #default="{ row }">
                  <el-switch 
                    v-model="row.is_active" 
                    @change="togglePeriodStatus(row)"
                    :loading="row.statusLoading"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button size="small" @click="editPeriod(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deletePeriod(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 绩效模板管理 -->
        <el-tab-pane label="绩效模板" name="templates">
          <div class="tab-content">
            <div class="tab-header">
              <h3>绩效模板管理</h3>
              <el-button type="primary" @click="showAddTemplateDialog">
                <el-icon><Plus /></el-icon>
                新建模板
              </el-button>
            </div>
            
            <el-table :data="templates" v-loading="templatesLoading" stripe>
              <el-table-column prop="name" label="模板名称" />
              <el-table-column prop="description" label="描述" show-overflow-tooltip />
              <el-table-column prop="total_score" label="总分" width="80" />
              <el-table-column label="指标数量" width="100">
                <template #default="{ row }">
                  <el-tag>{{ getIndicatorCount(row.id) }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="is_active" label="状态" width="80">
                <template #default="{ row }">
                  <el-switch 
                    v-model="row.is_active" 
                    @change="toggleTemplateStatus(row)"
                    :loading="row.statusLoading"
                  />
                </template>
              </el-table-column>
              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="viewTemplate(row)">查看</el-button>
                  <el-button size="small" @click="editTemplate(row)">编辑</el-button>
                  <el-button size="small" type="danger" @click="deleteTemplate(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 绩效目标管理 -->
        <el-tab-pane label="绩效目标" name="goals">
          <div class="tab-content">
            <div class="tab-header">
              <h3>绩效目标管理</h3>
              <div class="filter-group">
                <el-select v-model="goalFilter.period" placeholder="选择周期" clearable>
                  <el-option 
                    v-for="period in periods" 
                    :key="period.id" 
                    :label="period.name" 
                    :value="period.id"
                  />
                </el-select>
                <el-select v-model="goalFilter.status" placeholder="选择状态" clearable>
                  <el-option label="草稿" value="draft" />
                  <el-option label="已提交" value="submitted" />
                  <el-option label="已批准" value="approved" />
                  <el-option label="已拒绝" value="rejected" />
                </el-select>
                <el-button @click="filterGoals">筛选</el-button>
              </div>
            </div>
            
            <el-table :data="goals" v-loading="goalsLoading" stripe>
              <el-table-column prop="user_name" label="员工" />
              <el-table-column prop="period_name" label="周期" />
              <el-table-column prop="template_name" label="模板" />
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)">
                    {{ getStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="created_at" label="创建时间">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </el-table-column>              <el-table-column label="操作" width="250">
                <template #default="{ row }">
                  <el-button size="small" @click="viewGoal(row)">查看</el-button>
                  <el-button 
                    v-if="row.status === 'submitted'" 
                    size="small" 
                    type="success" 
                    @click="showApprovalDialog(row)"
                  >
                    审批
                  </el-button>
                  <el-button size="small" type="danger" @click="deleteGoal(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>

        <!-- 绩效评估管理 -->
        <el-tab-pane label="绩效评估" name="evaluations">
          <div class="tab-content">
            <div class="tab-header">
              <h3>绩效评估管理</h3>
              <div class="filter-group">
                <el-select v-model="evaluationFilter.period" placeholder="选择周期" clearable>
                  <el-option 
                    v-for="period in periods" 
                    :key="period.id" 
                    :label="period.name" 
                    :value="period.id"
                  />
                </el-select>
                <el-select v-model="evaluationFilter.status" placeholder="选择状态" clearable>
                  <el-option label="草稿" value="draft" />
                  <el-option label="自评完成" value="self_evaluated" />
                  <el-option label="上级评估完成" value="manager_evaluated" />
                  <el-option label="已完成" value="finalized" />
                </el-select>
                <el-button @click="filterEvaluations">筛选</el-button>
              </div>
            </div>
            
            <el-table :data="evaluations" v-loading="evaluationsLoading" stripe>
              <el-table-column prop="user_name" label="员工" />
              <el-table-column prop="period_name" label="周期" />
              <el-table-column prop="self_evaluation_score" label="自评分数" width="100">
                <template #default="{ row }">
                  <span v-if="row.self_evaluation_score">{{ row.self_evaluation_score }}</span>
                  <span v-else class="text-muted">未评估</span>
                </template>
              </el-table-column>
              <el-table-column prop="manager_evaluation_score" label="上级评分" width="100">
                <template #default="{ row }">
                  <span v-if="row.manager_evaluation_score">{{ row.manager_evaluation_score }}</span>
                  <span v-else class="text-muted">未评估</span>
                </template>
              </el-table-column>
              <el-table-column prop="final_score" label="最终得分" width="100">
                <template #default="{ row }">
                  <span v-if="row.final_score" class="final-score">{{ row.final_score }}</span>
                  <span v-else class="text-muted">未完成</span>
                </template>
              </el-table-column>
              <el-table-column prop="final_rating" label="等级" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.final_rating" :type="getRatingTagType(row.final_rating)">
                    {{ getRatingLabel(row.final_rating) }}
                  </el-tag>
                  <span v-else class="text-muted">未评级</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态">
                <template #default="{ row }">
                  <el-tag :type="getStatusTagType(row.status)">
                    {{ getStatusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>              <el-table-column label="操作" width="200">
                <template #default="{ row }">
                  <el-button size="small" @click="viewEvaluation(row)">查看详情</el-button>
                  <el-button 
                    v-if="row.status === 'self_evaluated'" 
                    size="small" 
                    type="primary" 
                    @click="startManagerEvaluation(row)"
                  >
                    上级评分
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>        <!-- 绩效统计 -->
        <el-tab-pane label="绩效统计" name="statistics">
          <div class="tab-content" v-loading="statisticsLoading">
            <div class="tab-header">
              <h3>绩效统计分析</h3>
              <el-button @click="loadStatistics" :loading="statisticsLoading">刷新数据</el-button>
            </div>
            
            <!-- 统计概览 -->
            <el-row :gutter="20" class="stats-overview">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon">
                      <el-icon size="24" color="#409EFF"><Document /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ performanceStats.total_evaluations }}</div>
                      <div class="stat-label">总评估数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon">
                      <el-icon size="24" color="#67C23A"><CircleCheck /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ performanceStats.completed_evaluations }}</div>
                      <div class="stat-label">完成评估</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon">
                      <el-icon size="24" color="#E6A23C"><TrendCharts /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ performanceStats.completion_rate }}%</div>
                      <div class="stat-label">完成率</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-icon">
                      <el-icon size="24" color="#F56C6C"><Star /></el-icon>
                    </div>
                    <div class="stat-info">
                      <div class="stat-value">{{ performanceStats.average_score }}</div>
                      <div class="stat-label">平均分数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 图表部分 -->
            <el-row :gutter="20">
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>绩效等级分布</span>
                  </template>
                  <div class="chart-container">
                    <div v-if="Object.keys(performanceStats.rating_distribution).length === 0" class="chart-placeholder">
                      暂无评级数据
                    </div>
                    <div v-else class="rating-distribution">
                      <div v-for="(count, rating) in performanceStats.rating_distribution" :key="rating" class="rating-item">
                        <div class="rating-label">{{ rating }}</div>
                        <div class="rating-bar">
                          <div class="rating-bar-fill" :style="{ width: calculateRatingPercentage(count) + '%' }"></div>
                        </div>
                        <div class="rating-count">{{ count }}</div>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="12">
                <el-card>
                  <template #header>
                    <span>部门绩效对比</span>
                  </template>
                  <div class="chart-container">
                    <div v-if="performanceStats.department_stats.length === 0" class="chart-placeholder">
                      暂无部门数据
                    </div>
                    <div v-else class="department-stats">
                      <div v-for="dept in performanceStats.department_stats" :key="dept.department" class="dept-item">
                        <div class="dept-name">{{ dept.department }}</div>
                        <div class="dept-info">
                          <span>完成: {{ dept.completed_evaluations }}/{{ dept.total_evaluations }}</span>
                          <span>完成率: {{ dept.completion_rate }}%</span>
                          <span>平均分: {{ dept.average_score }}</span>
                        </div>
                        <div class="dept-progress">
                          <el-progress :percentage="dept.completion_rate" :stroke-width="8" />
                        </div>
                      </div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>    <!-- 新建/编辑周期对话框 -->
    <el-dialog 
      v-model="addPeriodDialogVisible" 
      :title="editingPeriodId ? '编辑绩效周期' : '新建绩效周期'" 
      width="500px"
      :before-close="handleAddPeriodClose"
    >
      <el-form :model="periodForm" :rules="periodRules" ref="periodFormRef" label-width="100px">
        <el-form-item label="周期名称" prop="name">
          <el-input v-model="periodForm.name" placeholder="请输入周期名称" />
        </el-form-item>
        <el-form-item label="周期类型" prop="period_type">
          <el-select v-model="periodForm.period_type" placeholder="选择周期类型">
            <el-option label="月度" value="monthly" />
            <el-option label="季度" value="quarterly" />
            <el-option label="年度" value="yearly" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker
            v-model="periodForm.start_date"
            type="date"
            placeholder="选择开始日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期" prop="end_date">
          <el-date-picker
            v-model="periodForm.end_date"
            type="date"
            placeholder="选择结束日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="periodForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addPeriodDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitPeriod" :loading="periodSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新建/编辑模板对话框 -->
    <el-dialog 
      v-model="addTemplateDialogVisible" 
      :title="editingTemplateId ? '编辑绩效模板' : '新建绩效模板'" 
      width="500px"
      :before-close="handleAddTemplateClose"
    >
      <el-form :model="templateForm" :rules="templateRules" ref="templateFormRef" label-width="100px">
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="templateForm.name" placeholder="请输入模板名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="templateForm.description" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="总分" prop="total_score">
          <el-input-number v-model="templateForm.total_score" :min="0" :max="1000" />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="templateForm.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addTemplateDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitTemplate" :loading="templateSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新建/编辑目标对话框 -->
    <el-dialog 
      v-model="addGoalDialogVisible" 
      :title="editingGoalId ? '编辑绩效目标' : '新建绩效目标'" 
      width="500px"
      :before-close="handleAddGoalClose"
    >
      <el-form :model="goalForm" :rules="goalRules" ref="goalFormRef" label-width="100px">
        <el-form-item label="选择周期" prop="period">
          <el-select v-model="goalForm.period" placeholder="选择绩效周期">
            <el-option 
              v-for="period in periods" 
              :key="period.id" 
              :label="period.name" 
              :value="period.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择模板" prop="template">
          <el-select v-model="goalForm.template" placeholder="选择绩效模板">
            <el-option 
              v-for="template in templates" 
              :key="template.id" 
              :label="template.name" 
              :value="template.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="选择员工" prop="user">
          <el-select v-model="goalForm.user" placeholder="选择员工">            <el-option 
              v-for="user in allUsers" 
              :key="user.id" 
              :label="user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username" 
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="goalForm.status" placeholder="选择状态">
            <el-option label="草稿" value="draft" />
            <el-option label="已提交" value="submitted" />
            <el-option label="已批准" value="approved" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addGoalDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitGoal" :loading="goalSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新建/编辑评估对话框 -->
    <el-dialog 
      v-model="addEvaluationDialogVisible" 
      :title="editingEvaluationId ? '编辑绩效评估' : '新建绩效评估'" 
      width="500px"
      :before-close="handleAddEvaluationClose"
    >
      <el-form :model="evaluationForm" :rules="evaluationRules" ref="evaluationFormRef" label-width="100px">
        <el-form-item label="选择目标" prop="goal">
          <el-select v-model="evaluationForm.goal" placeholder="选择绩效目标">
            <el-option 
              v-for="goal in goals" 
              :key="goal.id" 
              :label="goal.user_name + ' - ' + goal.period_name" 
              :value="goal.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="evaluationForm.status" placeholder="选择状态">
            <el-option label="待评估" value="pending" />
            <el-option label="已完成" value="finalized" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="addEvaluationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitEvaluation" :loading="evaluationSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 审批对话框 -->
    <el-dialog 
      v-model="approvalDialogVisible" 
      title="审批绩效目标" 
      width="400px"
      :before-close="handleApprovalClose"
    >
      <el-form :model="approvalForm" :rules="approvalRules" ref="approvalFormRef" label-width="100px">
        <el-form-item label="审批状态" prop="status">
          <el-select v-model="approvalForm.status" placeholder="选择审批状态">
            <el-option label="通过" value="approved" />
            <el-option label="拒绝" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item label="审批备注" prop="note">
          <el-input 
            v-model="approvalForm.note" 
            type="textarea" 
            placeholder="请输入审批备注（可选）" 
            rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="approvalDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitApproval" :loading="approvalSubmitting">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 上级评分对话框 -->
    <el-dialog 
      v-model="managerEvaluationDialogVisible" 
      title="上级评分" 
      width="800px"
      :before-close="handleManagerEvaluationClose"
    >
      <div v-if="currentEvaluation">
        <el-card style="margin-bottom: 20px;">
          <template #header>
            <span>员工信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="员工姓名">
              {{ currentEvaluation.employee_name }}
            </el-descriptions-item>
            <el-descriptions-item label="考核周期">
              {{ currentEvaluation.period_name }}
            </el-descriptions-item>
            <el-descriptions-item label="自评分数">
              {{ currentEvaluation.self_evaluation_score || '未自评' }}
            </el-descriptions-item>
            <el-descriptions-item label="自评时间">
              {{ formatDate(currentEvaluation.self_evaluated_at) || '未自评' }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div v-if="currentEvaluation.self_evaluation_comment" style="margin-top: 15px;">
            <p><strong>自评总结：</strong></p>
            <p style="background: #f5f5f5; padding: 10px; border-radius: 4px;">
              {{ currentEvaluation.self_evaluation_comment }}
            </p>
          </div>
        </el-card>

        <el-form :model="managerEvaluationForm" :rules="managerEvaluationRules" ref="managerEvaluationFormRef" label-width="120px">
          <!-- 明细评分 -->
          <el-card style="margin-bottom: 20px;">
            <template #header>
              <span>指标评分</span>
            </template>
            
            <div v-for="(detail, index) in managerEvaluationForm.details" :key="detail.id" style="margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
              <h4>{{ detail.indicator_name }}</h4>
              <p class="indicator-desc">{{ detail.indicator_description }}</p>
              
              <el-row :gutter="20">
                <el-col :span="12">
                  <p><strong>员工自评：</strong>{{ detail.self_score || '未评分' }}分</p>
                  <p v-if="detail.self_comment" style="background: #f0f9ff; padding: 8px; border-radius: 4px; font-size: 12px;">
                    {{ detail.self_comment }}
                  </p>
                </el-col>
                <el-col :span="12">
                  <el-form-item :label="'上级评分'" :prop="'details.' + index + '.manager_score'" :rules="[{ required: true, message: '请输入评分', trigger: 'blur' }]">
                    <el-input-number 
                      v-model="detail.manager_score" 
                      :min="0" 
                      :max="100" 
                      placeholder="请输入分数"
                      style="width: 100%;"
                    />
                  </el-form-item>
                  <el-form-item :label="'评价说明'" :prop="'details.' + index + '.manager_comment'">
                    <el-input 
                      v-model="detail.manager_comment" 
                      type="textarea" 
                      :rows="2"
                      placeholder="请输入评价说明"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </div>
          </el-card>

          <!-- 总体评分 -->
          <el-card>
            <template #header>
              <span>总体评价</span>
            </template>
            
            <el-form-item label="上级评分" prop="manager_evaluation_score" :rules="[{ required: true, message: '请输入总体评分', trigger: 'blur' }]">
              <el-input-number 
                v-model="managerEvaluationForm.manager_evaluation_score" 
                :min="0" 
                :max="100" 
                placeholder="请输入总体评分"
                style="width: 200px;"
              />
              <span style="margin-left: 10px; color: #999;">分</span>
            </el-form-item>
            
            <el-form-item label="最终等级" prop="final_rating">
              <el-select v-model="managerEvaluationForm.final_rating" placeholder="请选择最终等级" style="width: 200px;">
                <el-option label="优秀" value="excellent" />
                <el-option label="良好" value="good" />
                <el-option label="一般" value="average" />
                <el-option label="差" value="poor" />
              </el-select>
            </el-form-item>
            
            <el-form-item label="评价总结" prop="manager_evaluation_comment">
              <el-input 
                v-model="managerEvaluationForm.manager_evaluation_comment" 
                type="textarea" 
                :rows="4"
                placeholder="请输入对员工本期表现的总体评价..."
              />
            </el-form-item>
          </el-card>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="managerEvaluationDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitManagerEvaluation" :loading="managerEvaluationSubmitting">提交评分</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Calendar,
  Document,
  Star,
  Plus,
  CircleCheck,
  TrendCharts
} from '@element-plus/icons-vue'
import api from '@/utils/api'
import { useAuthStore } from '@/stores/counter'

// 使用认证store
const authStore = useAuthStore()

// 响应式数据
const activeTab = ref('periods')
const periodsLoading = ref(false)
const templatesLoading = ref(false)
const goalsLoading = ref(false)
const evaluationsLoading = ref(false)

// 统计数据
const stats = reactive({
  totalPeriods: 0,
  totalTemplates: 0,
  totalGoals: 0,
  totalEvaluations: 0
})

// 绩效统计数据
const performanceStats = reactive({
  total_evaluations: 0,
  completed_evaluations: 0,
  completion_rate: 0,
  average_score: 0,
  rating_distribution: {} as Record<string, number>,
  department_stats: [] as Array<{
    department: string;
    total_evaluations: number;
    completed_evaluations: number;
    completion_rate: number;
    average_score: number;
  }>
})

const statisticsLoading = ref(false)

// 数据列表
const periods = ref<any[]>([])
const templates = ref<any[]>([])
const goals = ref<any[]>([])
const evaluations = ref<any[]>([])
const allUsers = ref<any[]>([])

// 筛选条件
const goalFilter = reactive({
  period: '',
  status: ''
})

const evaluationFilter = reactive({
  period: '',
  status: ''
})

// 上级评分对话框
const managerEvaluationDialogVisible = ref(false)
const managerEvaluationSubmitting = ref(false)
const managerEvaluationFormRef = ref()
const currentEvaluation = ref<any>(null)

const managerEvaluationForm = reactive({
  manager_evaluation_score: null as number | null,
  manager_evaluation_comment: '',
  final_rating: '',
  details: [] as any[]
})

const managerEvaluationRules = {
  manager_evaluation_score: [
    { required: true, message: '请输入上级评分', trigger: 'blur' }
  ],
  manager_evaluation_comment: [
    { required: true, message: '请输入评价总结', trigger: 'blur' }
  ],
  final_rating: [
    { required: true, message: '请选择最终等级', trigger: 'change' }
  ]
}

// 新建周期对话框
const addPeriodDialogVisible = ref(false)
const periodSubmitting = ref(false)
const periodFormRef = ref()
const editingPeriodId = ref<number | null>(null)

const periodForm = reactive({
  name: '',
  period_type: '',
  start_date: null as Date | string | null,
  end_date: null as Date | string | null,
  is_active: true
})

const periodRules = {
  name: [{ required: true, message: '请输入周期名称', trigger: 'blur' }],
  period_type: [{ required: true, message: '请选择周期类型', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

// 新建模板对话框
const addTemplateDialogVisible = ref(false)
const templateSubmitting = ref(false)
const templateFormRef = ref()
const editingTemplateId = ref<number | null>(null)

const templateForm = reactive({
  name: '',
  description: '',
  total_score: 100,
  is_active: true
})

const templateRules = {
  name: [{ required: true, message: '请输入模板名称', trigger: 'blur' }],
  total_score: [{ required: true, message: '请输入总分', trigger: 'blur' }]
}

// 新建目标对话框
const addGoalDialogVisible = ref(false)
const goalSubmitting = ref(false)
const goalFormRef = ref()
const editingGoalId = ref<number | null>(null)

const goalForm = reactive({
  period: '',
  template: '',
  user: '',
  status: 'draft'
})

const goalRules = {
  period: [{ required: true, message: '请选择绩效周期', trigger: 'change' }],
  template: [{ required: true, message: '请选择绩效模板', trigger: 'change' }],
  user: [{ required: true, message: '请选择员工', trigger: 'change' }]
}

// 新建评估对话框
const addEvaluationDialogVisible = ref(false)
const evaluationSubmitting = ref(false)
const evaluationFormRef = ref()
const editingEvaluationId = ref<number | null>(null)

const evaluationForm = reactive({
  goal: '',
  status: 'pending'
})

const evaluationRules = {
  goal: [{ required: true, message: '请选择绩效目标', trigger: 'change' }]
}

// 审批对话框
const approvalDialogVisible = ref(false)
const approvalSubmitting = ref(false)
const approvalFormRef = ref()
const currentApprovalGoal = ref<any>(null)

const approvalForm = reactive({
  status: 'approved',
  note: ''
})

const approvalRules = {
  status: [{ required: true, message: '请选择审批状态', trigger: 'change' }]
}

// 生命周期
onMounted(async () => {
  console.log('绩效管理页面mounted')
  
  // 检查认证状态
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，尝试初始化认证状态...')
    authStore.initAuth()
    
    // 等待一小段时间让认证状态初始化
    await new Promise(resolve => setTimeout(resolve, 100))
  }
  
  console.log('用户认证状态:', authStore.isAuthenticated)
  console.log('用户类型:', authStore.user?.user_type)
  
  if (!authStore.isAuthenticated) {
    ElMessage.error('用户未登录，请先登录')
    return
  }
  
  if (authStore.user?.user_type !== 'admin') {
    ElMessage.error('无权限访问此页面')
    return
  }
  
  console.log('开始加载数据...')
  loadData()
})

// 方法
const loadData = async () => {
  await Promise.all([
    loadPeriods(),
    loadTemplates(),
    loadGoals(),
    loadEvaluations(),
    loadAllUsers()
  ])
  updateStats()
}

const loadPeriods = async () => {
  periodsLoading.value = true
  try {
    const response = await api.get('/performance/periods/')
    periods.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载绩效周期失败:', error)
    ElMessage.error('加载绩效周期失败')
  } finally {
    periodsLoading.value = false
  }
}

const loadTemplates = async () => {
  templatesLoading.value = true
  try {
    const response = await api.get('/performance/templates/')
    templates.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载绩效模板失败:', error)
    ElMessage.error('加载绩效模板失败')
  } finally {
    templatesLoading.value = false
  }
}

const loadGoals = async () => {
  goalsLoading.value = true
  try {
    const params: any = {}
    if (goalFilter.period) params.period_id = goalFilter.period
    if (goalFilter.status) params.status = goalFilter.status
    
    const response = await api.get('/performance/goals/', { params })
    goals.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载绩效目标失败:', error)
    ElMessage.error('加载绩效目标失败')
  } finally {
    goalsLoading.value = false
  }
}

const loadEvaluations = async () => {
  evaluationsLoading.value = true
  try {
    const response = await api.get('/performance/evaluations/')
    evaluations.value = response.data.results || response.data || []
  } catch (error) {
    console.error('加载绩效评估失败:', error)
    ElMessage.error('加载绩效评估失败')
  } finally {
    evaluationsLoading.value = false
  }
}

const loadAllUsers = async () => {
  try {
    console.log('开始加载用户列表...')
    
    // 检查认证状态
    const token = localStorage.getItem('access_token')
    if (!token) {
      console.error('未找到认证token')
      ElMessage.error('用户未认证，请重新登录')
      return
    }
    
    console.log('认证token存在，token前缀:', token.substring(0, 20) + '...')
    
    const response = await api.get('/auth/users/')
    console.log('用户列表API响应:', response.status, response.data)
    
    allUsers.value = response.data.results || response.data || []
    console.log('用户列表加载成功，用户数量:', allUsers.value.length)
      } catch (error: any) {
    console.error('加载用户列表失败:', error)
    
    if (error.response?.status === 401) {
      ElMessage.error('认证已过期，请重新登录')
      // 清除无效token
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } else {
      ElMessage.error('加载用户列表失败: ' + (error.response?.data?.message || error.message))
    }
  }
}

const updateStats = () => {
  stats.totalPeriods = periods.value.length
  stats.totalTemplates = templates.value.length
  stats.totalGoals = goals.value.length
  stats.totalEvaluations = evaluations.value.length
}

// 加载绩效统计数据
const loadStatistics = async () => {
  if (statisticsLoading.value) return
  
  statisticsLoading.value = true
  try {
    console.log('加载绩效统计数据...')
    const response = await api.get('/performance/evaluations/statistics/')
    
    // 更新统计数据
    Object.assign(performanceStats, response.data)
    
    console.log('绩效统计数据加载完成:', performanceStats)
    ElMessage.success('统计数据加载完成')  } catch (error: any) {
    console.error('加载绩效统计失败:', error)
    ElMessage.error('加载统计数据失败: ' + (error.response?.data?.message || error.message))  } finally {
    statisticsLoading.value = false
  }
}

// 计算评级百分比
const calculateRatingPercentage = (count: number) => {
  const total = performanceStats.total_evaluations
  if (total === 0) return 0
  return Math.round((count / total) * 100)
}

const handleTabClick = (tab: any) => {
  console.log('切换到标签页:', tab.name)
  if (tab.name === 'statistics') {
    loadStatistics()
  }
}

const showAddPeriodDialog = () => {
  // 重置表单
  Object.assign(periodForm, {
    name: '',
    period_type: '',
    start_date: null,
    end_date: null,
    is_active: true
  })
  editingPeriodId.value = null
  addPeriodDialogVisible.value = true
}

const handleAddPeriodClose = () => {
  periodFormRef.value?.resetFields()
  editingPeriodId.value = null
  addPeriodDialogVisible.value = false
}

const submitPeriod = async () => {
  if (!periodFormRef.value) return
  
  const valid = await periodFormRef.value.validate()
  if (!valid) return
  
  periodSubmitting.value = true
  try {
    // 格式化日期数据 - 确保日期格式正确
    const formData = {
      ...periodForm,
      start_date: periodForm.start_date ? 
        (periodForm.start_date instanceof Date ? 
          periodForm.start_date.toISOString().split('T')[0] : 
          periodForm.start_date) : null,
      end_date: periodForm.end_date ? 
        (periodForm.end_date instanceof Date ? 
          periodForm.end_date.toISOString().split('T')[0] : 
          periodForm.end_date) : null
    }
    
    console.log('提交的数据:', formData)
    console.log('用户认证状态:', localStorage.getItem('access_token') ? '已认证' : '未认证')
    
    let response;
    if (editingPeriodId.value) {
      // 编辑模式
      response = await api.patch(`/performance/periods/${editingPeriodId.value}/`, formData)
      ElMessage.success('绩效周期更新成功')
    } else {
      // 新建模式
      response = await api.post('/performance/periods/', formData)
      ElMessage.success('绩效周期创建成功')
    }
    
    console.log('API响应:', response)
    addPeriodDialogVisible.value = false
    await loadPeriods()
    updateStats()
  } catch (error: any) {
    console.error('创建绩效周期失败:', error)
    console.error('错误详情:', {
      message: error.message,
      response: error.response?.data,
      status: error.response?.status,
      url: error.config?.url,
      method: error.config?.method
    })
    
    let errorMsg = '操作失败'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail
      } else {
        // 处理字段验证错误
        const errors = []
        for (const [field, messages] of Object.entries(error.response.data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`)
          } else {
            errors.push(`${field}: ${messages}`)
          }
        }
        errorMsg = errors.length > 0 ? errors.join('\n') : JSON.stringify(error.response.data)
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    ElMessage.error(errorMsg)
  } finally {
    periodSubmitting.value = false
  }
}

const togglePeriodStatus = async (period: any) => {
  period.statusLoading = true
  try {
    await api.patch(`/performance/periods/${period.id}/`, {
      is_active: period.is_active
    })
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('更新周期状态失败:', error)
    ElMessage.error('更新状态失败')
    period.is_active = !period.is_active // 恢复原状态
  } finally {
    period.statusLoading = false
  }
}

const toggleTemplateStatus = async (template: any) => {
  template.statusLoading = true
  try {
    await api.patch(`/performance/templates/${template.id}/`, {
      is_active: template.is_active
    })
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('更新模板状态失败:', error)
    ElMessage.error('更新状态失败')
    template.is_active = !template.is_active // 恢复原状态
  } finally {
    template.statusLoading = false
  }
}

const editPeriod = (period: any) => {
  // 编辑绩效周期功能
  Object.assign(periodForm, {
    name: period.name,
    period_type: period.period_type,
    start_date: new Date(period.start_date),
    end_date: new Date(period.end_date),
    is_active: period.is_active
  })
  
  // 设置为编辑模式
  editingPeriodId.value = period.id
  addPeriodDialogVisible.value = true
}

const deletePeriod = async (period: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个绩效周期吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/performance/periods/${period.id}/`)
    ElMessage.success('删除成功')
    await loadPeriods()
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除周期失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const showAddTemplateDialog = () => {
  templateForm.name = ''
  templateForm.description = ''
  templateForm.total_score = 100
  templateForm.is_active = true
  editingTemplateId.value = null
  addTemplateDialogVisible.value = true
}

const editTemplate = (template: any) => {
  Object.assign(templateForm, {
    name: template.name,
    description: template.description || '',
    total_score: template.total_score,
    is_active: template.is_active
  })
  
  editingTemplateId.value = template.id
  addTemplateDialogVisible.value = true
}

const handleAddTemplateClose = () => {
  templateFormRef.value?.resetFields()
  editingTemplateId.value = null
  addTemplateDialogVisible.value = false
}

const submitTemplate = async () => {
  if (!templateFormRef.value) return
  
  const valid = await templateFormRef.value.validate()
  if (!valid) return
  
  templateSubmitting.value = true
  try {
    const formData = { ...templateForm }
    
    console.log('提交的模板数据:', formData)
    
    if (editingTemplateId.value) {
      // 编辑模式
      await api.patch(`/performance/templates/${editingTemplateId.value}/`, formData)
      ElMessage.success('绩效模板更新成功')
    } else {
      // 新建模式
      await api.post('/performance/templates/', formData)
      ElMessage.success('绩效模板创建成功')
    }
    
    addTemplateDialogVisible.value = false
    await loadTemplates()
    updateStats()
  } catch (error: any) {
    console.error('操作绩效模板失败:', error)
    
    let errorMsg = '操作失败'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail
      } else {
        const errors = []
        for (const [field, messages] of Object.entries(error.response.data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`)
          } else {
            errors.push(`${field}: ${messages}`)
          }
        }
        errorMsg = errors.length > 0 ? errors.join('\n') : JSON.stringify(error.response.data)
      }
    } else if (error.message) {
      errorMsg = error.message
    }
    
    ElMessage.error(errorMsg)
  } finally {
    templateSubmitting.value = false
  }
}

const toggleGoalStatus = async (goal: any) => {
  goal.statusLoading = true
  try {
    await api.patch(`/performance/goals/${goal.id}/`, {
      status: goal.status
    })
    ElMessage.success('状态更新成功')
  } catch (error) {
    console.error('更新目标状态失败:', error)
    ElMessage.error('更新状态失败')
    goal.status = goal.status === 'active' ? 'inactive' : 'active' // 恢复原状态
  } finally {
    goal.statusLoading = false
  }
}

const showAddGoalDialog = () => {
  goalForm.period = ''
  goalForm.template = ''
  goalForm.user = ''
  goalForm.status = 'draft'
  editingGoalId.value = null
  addGoalDialogVisible.value = true
}

const handleAddGoalClose = () => {
  goalFormRef.value?.resetFields()
  editingGoalId.value = null
  addGoalDialogVisible.value = false
}

const submitGoal = async () => {
  if (!goalFormRef.value) return
  
  const valid = await goalFormRef.value.validate()
  if (!valid) return
  
  goalSubmitting.value = true
  try {
    const formData = { ...goalForm }
    
    console.log('提交的目标数据:', formData)
    
    if (editingGoalId.value) {
      await api.patch(`/performance/goals/${editingGoalId.value}/`, formData)
      ElMessage.success('绩效目标更新成功')
    } else {
      await api.post('/performance/goals/', formData)
      ElMessage.success('绩效目标创建成功')
    }
    
    addGoalDialogVisible.value = false
    await loadGoals()
    updateStats()
  } catch (error: any) {
    console.error('操作绩效目标失败:', error)
    
    let errorMsg = '操作失败'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail
      } else {
        const errors = []
        for (const [field, messages] of Object.entries(error.response.data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`)
          } else {
            errors.push(`${field}: ${messages}`)
          }
        }
        errorMsg = errors.length > 0 ? errors.join('\n') : JSON.stringify(error.response.data)
      }
    }
    
    ElMessage.error(errorMsg)
  } finally {
    goalSubmitting.value = false
  }
}

const showAddEvaluationDialog = () => {
  evaluationForm.goal = ''
  evaluationForm.status = 'pending'
  editingEvaluationId.value = null
  addEvaluationDialogVisible.value = true
}

const handleAddEvaluationClose = () => {
  evaluationFormRef.value?.resetFields()
  editingEvaluationId.value = null
  addEvaluationDialogVisible.value = false
}

const submitEvaluation = async () => {
  if (!evaluationFormRef.value) return
  
  const valid = await evaluationFormRef.value.validate()
  if (!valid) return
  
  evaluationSubmitting.value = true
  try {
    const formData = { ...evaluationForm }
    
    console.log('提交的评估数据:', formData)
    
    if (editingEvaluationId.value) {
      await api.patch(`/performance/evaluations/${editingEvaluationId.value}/`, formData)
      ElMessage.success('绩效评估更新成功')
    } else {
      await api.post('/performance/evaluations/', formData)
      ElMessage.success('绩效评估创建成功')
    }
    
    addEvaluationDialogVisible.value = false
    await loadEvaluations()
    updateStats()
  } catch (error: any) {
    console.error('操作绩效评估失败:', error)
    
    let errorMsg = '操作失败'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail
      } else {
        const errors = []
        for (const [field, messages] of Object.entries(error.response.data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`)
          } else {
            errors.push(`${field}: ${messages}`)
          }
        }
        errorMsg = errors.length > 0 ? errors.join('\n') : JSON.stringify(error.response.data)
      }
    }
    
    ElMessage.error(errorMsg)
  } finally {
    evaluationSubmitting.value = false
  }
}

const submitApproval = async () => {
  const goal = currentApprovalGoal.value
  if (!goal) return
  
  approvalSubmitting.value = true
  try {
    const formData = {
      status: approvalForm.status,
      note: approvalForm.note || ''
    }
    
    console.log('提交的审批数据:', formData)
    
    // 使用正确的审批接口
    await api.post(`/performance/goals/${goal.id}/approve/`, formData)
    ElMessage.success('审批操作成功')
    
    // 刷新目标列表
    await loadGoals()
  } catch (error: any) {
    console.error('操作审批失败:', error)
    
    let errorMsg = '操作失败'
    if (error.response?.data) {
      if (typeof error.response.data === 'string') {
        errorMsg = error.response.data
      } else if (error.response.data.detail) {
        errorMsg = error.response.data.detail
      } else if (error.response.data.error) {
        errorMsg = error.response.data.error
      } else {
        const errors = []
        for (const [field, messages] of Object.entries(error.response.data)) {
          if (Array.isArray(messages)) {
            errors.push(`${field}: ${messages.join(', ')}`)
          } else {
            errors.push(`${field}: ${messages}`)
          }
        }
        errorMsg = errors.length > 0 ? errors.join('\n') : JSON.stringify(error.response.data)
      }
    }
    
    ElMessage.error(errorMsg)
  } finally {
    approvalSubmitting.value = false
    approvalDialogVisible.value = false
  }
}

// 显示审批对话框
const showApprovalDialog = (goal: any) => {
  currentApprovalGoal.value = goal
  approvalForm.status = 'approved'
  approvalForm.note = ''
  approvalDialogVisible.value = true
}

// 处理审批对话框关闭
const handleApprovalClose = (done: Function) => {
  if (approvalSubmitting.value) {
    ElMessage.warning('正在提交，请稍候...')
    return
  }
  done()
}

// 模板相关方法
const viewTemplate = (template: any) => {
  // 查看模板详情
  ElMessageBox.alert(
    `<div style="text-align: left;">
      <h4>${template.name}</h4>
      <p><strong>描述：</strong>${template.description || '无'}</p>
      <p><strong>总分：</strong>${template.total_score}</p>
      <p><strong>状态：</strong>${template.is_active ? '启用' : '禁用'}</p>
      <p><strong>创建时间：</strong>${new Date(template.created_at).toLocaleString()}</p>
    </div>`,
    '模板详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭'
    }
  )
}

const deleteTemplate = async (template: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个绩效模板吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/performance/templates/${template.id}/`)
    ElMessage.success('删除成功')
    await loadTemplates()
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除模板失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 目标相关方法
const filterGoals = () => {
  loadGoals()
}

const viewGoal = (goal: any) => {
  // 查看目标详情
  let detailsHtml = `<div style="text-align: left;">
    <h4>${goal.user_info?.full_name || goal.user_info?.username || '未知用户'} - 绩效目标</h4>
    <p><strong>绩效周期：</strong>${goal.period_name || '未指定'}</p>
    <p><strong>模板：</strong>${goal.template_name || '未指定'}</p>
    <p><strong>状态：</strong>${getStatusLabel(goal.status)}</p>
    <p><strong>审批人：</strong>${goal.approver_name || '未指定'}</p>
    <p><strong>创建时间：</strong>${new Date(goal.created_at).toLocaleString()}</p>`
  
  if (goal.details && goal.details.length > 0) {
    detailsHtml += '<br><h5>目标详情：</h5><ul>'
    goal.details.forEach((detail: any) => {
      detailsHtml += `<li>
        <strong>${detail.indicator_name}:</strong> 
        目标值: ${detail.target_value || 'N/A'}, 
        权重: ${detail.weight || 0}%, 
        最高分: ${detail.max_score || 0}
      </li>`
    })
    detailsHtml += '</ul>'
  }
  
  detailsHtml += '</div>'
  
  ElMessageBox.alert(detailsHtml, '绩效目标详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '关闭'
  })
}

const deleteGoal = async (goal: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这个绩效目标吗？', '确认删除', {
      type: 'warning'
    })
    
    await api.delete(`/performance/goals/${goal.id}/`)
    ElMessage.success('删除成功')
    await loadGoals()
    updateStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除目标失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 评估相关方法
const filterEvaluations = () => {
  loadEvaluations()
}

const viewEvaluation = (evaluation: any) => {
  // 查看评估详情
  let detailsHtml = `<div style="text-align: left;">
    <h4>绩效评估详情</h4>
    <p><strong>员工：</strong>${evaluation.goal?.user_info?.full_name || evaluation.goal?.user_info?.username || '未知用户'}</p>
    <p><strong>绩效周期：</strong>${evaluation.goal?.period_name || '未指定'}</p>
    <p><strong>评估状态：</strong>${getStatusLabel(evaluation.status)}</p>
    <p><strong>自评分数：</strong>${evaluation.self_score || 'N/A'}</p>
    <p><strong>上级评分：</strong>${evaluation.manager_score || 'N/A'}</p>
    <p><strong>最终分数：</strong>${evaluation.final_score || 'N/A'}</p>
    <p><strong>评估人：</strong>${evaluation.evaluator_name || '未指定'}</p>
    <p><strong>创建时间：</strong>${new Date(evaluation.created_at).toLocaleString()}</p>`
  
  if (evaluation.self_comment) {
    detailsHtml += `<br><p><strong>自评意见：</strong></p><p style="background: #f5f5f5; padding: 10px; border-radius: 4px;">${evaluation.self_comment}</p>`
  }
  
  if (evaluation.manager_comment) {
    detailsHtml += `<br><p><strong>上级评价：</strong></p><p style="background: #f5f5f5; padding: 10px; border-radius: 4px;">${evaluation.manager_comment}</p>`
  }
  
  if (evaluation.details && evaluation.details.length > 0) {
    detailsHtml += '<br><h5>评估详情：</h5><ul>'
    evaluation.details.forEach((detail: any) => {
      detailsHtml += `<li>
        <strong>${detail.indicator_name}:</strong> 
        自评: ${detail.self_score || 'N/A'}, 
        上级评分: ${detail.manager_score || 'N/A'}, 
        最终: ${detail.final_score || 'N/A'}
      </li>`
    })
    detailsHtml += '</ul>'
  }
  
  detailsHtml += '</div>'
  
  ElMessageBox.alert(detailsHtml, '绩效评估详情', {
    dangerouslyUseHTMLString: true,
    confirmButtonText: '关闭'
  })
}

// 辅助函数
const getPeriodTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    monthly: '月度',
    quarterly: '季度',
    yearly: '年度'
  }
  return labels[type] || type
}

const getPeriodTypeTagType = (type: string) => {
  const types: Record<string, string> = {
    monthly: '',
    quarterly: 'success',
    yearly: 'warning'
  }
  return types[type] || ''
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    submitted: '已提交',
    approved: '已批准',
    rejected: '已拒绝',
    self_evaluated: '自评完成',
    manager_evaluated: '上级评估完成',
    finalized: '已完成'
  }
  return labels[status] || status
}

const getStatusTagType = (status: string) => {
  const types: Record<string, string> = {
    draft: 'info',
    submitted: 'warning',
    approved: 'success',
    rejected: 'danger',
    self_evaluated: 'warning',
    manager_evaluated: 'primary',
    finalized: 'success'
  }
  return types[status] || 'info'
}

const getRatingLabel = (rating: string) => {
  const labels: Record<string, string> = {
    excellent: '优秀',
    good: '良好',
    average: '一般',
    poor: '待改进'
  }
  return labels[rating] || rating
}

const getRatingTagType = (rating: string) => {
  const types: Record<string, string> = {
    excellent: 'success',
    good: 'primary',
    average: 'warning',
    poor: 'danger'
  }
  return types[rating] || 'info'
}

const getIndicatorCount = (templateId: number) => {
  // 这里应该从API获取实际的指标数量
  return Math.floor(Math.random() * 8) + 3 // 临时模拟数据
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

// 上级评分相关方法
const startManagerEvaluation = async (evaluation: any) => {
  try {
    console.log('开始上级评分:', evaluation)
    
    // 获取评估详情
    const response = await api.get(`/performance/evaluations/${evaluation.id}/`)
    currentEvaluation.value = response.data
    
    // 初始化表单数据
    managerEvaluationForm.manager_evaluation_score = null
    managerEvaluationForm.manager_evaluation_comment = ''
    managerEvaluationForm.final_rating = ''
    managerEvaluationForm.details = currentEvaluation.value.details.map((detail: any) => ({
      id: detail.id,
      indicator_name: detail.indicator.name,
      indicator_description: detail.indicator.description,
      self_score: detail.self_score,
      self_comment: detail.self_comment,
      manager_score: detail.manager_score || null,
      manager_comment: detail.manager_comment || '',
      final_score: detail.final_score || null
    }))
    
    managerEvaluationDialogVisible.value = true
  } catch (error) {
    console.error('获取评估详情失败:', error)
    ElMessage.error('获取评估详情失败')
  }
}

const submitManagerEvaluation = async () => {
  if (!managerEvaluationFormRef.value) return
  
  try {
    await managerEvaluationFormRef.value.validate()
    managerEvaluationSubmitting.value = true
    
    const submitData = {
      manager_evaluation_score: managerEvaluationForm.manager_evaluation_score,
      manager_evaluation_comment: managerEvaluationForm.manager_evaluation_comment,
      final_rating: managerEvaluationForm.final_rating,
      details: managerEvaluationForm.details.map(detail => ({
        id: detail.id,
        manager_score: detail.manager_score,
        manager_comment: detail.manager_comment,
        final_score: detail.manager_score // 暂时将最终分数设为上级评分
      }))
    }
    
    await api.post(`/performance/evaluations/${currentEvaluation.value.id}/manager_evaluate/`, submitData)
    
    ElMessage.success('上级评分提交成功')
    managerEvaluationDialogVisible.value = false
    
    // 刷新评估列表
    await loadEvaluations()
  } catch (error) {
    console.error('提交上级评分失败:', error)
    ElMessage.error('提交上级评分失败')
  } finally {
    managerEvaluationSubmitting.value = false
  }
}

const handleManagerEvaluationClose = () => {
  managerEvaluationDialogVisible.value = false
  currentEvaluation.value = null
}
</script>

<style scoped>
.performance-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.header-content h2 {
  margin: 0 0 10px 0;
  color: #409EFF;
}

.header-content p {
  margin: 0;
  color: #666;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 15px;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409EFF;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.main-content {
  margin-bottom: 20px;
}

.tab-content {
  padding: 20px 0;
}

.tab-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tab-header h3 {
  margin: 0;
  color: #409EFF;
}

.filter-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-group .el-select {
  width: 150px;
}

.final-score {
  font-weight: bold;
  color: #67C23A;
}

.text-muted {
  color: #999;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  color: #ccc;
  font-size: 16px;
}

.stats-overview {
  margin-bottom: 20px;
}

.rating-distribution {
  padding: 20px;
}

.rating-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.rating-label {
  width: 80px;
  font-weight: 500;
  color: #333;
}

.rating-bar {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 10px;
  margin: 0 15px;
  overflow: hidden;
}

.rating-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #67C23A);
  border-radius: 10px;
  transition: width 0.3s ease;
}

.rating-count {
  width: 40px;
  text-align: center;
  font-weight: 500;
  color: #666;
}

.department-stats {
  padding: 20px;
}

.dept-item {
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.dept-name {
  font-weight: 500;
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.dept-info {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
  font-size: 12px;
  color: #666;
}

.dept-progress {
  margin-top: 10px;
}

.dialog-footer {
  text-align: right;
}
</style>
