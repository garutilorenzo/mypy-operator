% include('header.tpl')
<main class="container">
    <div class="row">
        <div class="col-12 text-center">
          <h1> Servers </h1>
        </div>
        <div class="col-12">
          <div class="row">
            <!-- Portfolio Item 1 -->
            % for server in servers:
            <div class="col-md-4 col-lg-4 mb-4">
                <p>
                    Server name: {{ server.server_name }} 
                </p>
                <p> 
                  % is_reachable = is_server_reachable(server.server_name)
                  % if is_reachable:
                  % badge_css = 'bg-success'
                  % state = 'Reachable'
                  % else:
                  % badge_css = 'bg-danger'
                  % state = 'Unreachable'
                  % end
                  State: <span class="badge rounded-pill {{ badge_css }}">{{ state }}</span> 
                </p>
                <a href="/server/{{ server.cluster.gr_name }}/{{ server.server_id }}" class="btn btn-primary btn-sm" title="Go to cluster  {{ server.server_name }} detail">Detail</a>
            </div>
            % end
          </div>
        </div>
    </div>
</main>
% include('footer.tpl')