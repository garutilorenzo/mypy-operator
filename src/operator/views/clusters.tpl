% include('header.tpl')
<main class="container">
    <div class="row">
        <div class="col-12 text-center">
          <h1> Clusters </h1>
        </div>
        <div class="col-12">
          <div class="row">
            <!-- Portfolio Item 1 -->
            % for cluster in clusters:
            <div class="col-md-4 col-lg-4 mb-4">
                <p>
                    Cluster name: {{ cluster.cluster_name }} 
                </p>
                <p> 
                  % if cluster.state == 'active':
                  % badge_css = 'bg-success'
                  % elif cluster.state == 'init':
                  % badge_css = 'bg-danger'
                  % end
                  State: <span class="badge rounded-pill {{ badge_css }}">{{ cluster.state }}</span> 
                </p>
                <p>
                    % servers = get_servers(cluster_name=cluster.cluster_name, output='web')
                    Cluster members: {{ len(servers) }}
                </p>
                <a href="/cluster/{{ cluster.gr_name }}" class="btn btn-primary btn-sm" title="Go to cluster {{ cluster.cluster_name }} detail">Detail</a>
            </div>
            % end
          </div>
        </div>
    </div>
</main>
% include('footer.tpl')